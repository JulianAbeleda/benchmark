//! HT-020 live headless driver, using GameTerm's shared production loop.
use gameterm_backend::{
    effects::CancellationToken, terminal_fake::fake_registry, BoundedText, CredentialRef, Endpoint,
    Id, ProviderProfile,
};
use gameterm_harness::{terminal::ToolResult, MinimalHarness};
use gameterm_host::terminal_coordinator::AskTerminalCoordinator;
use gameterm_host::terminal_session::TerminalSession;

fn id(value: &str) -> Id {
    Id::new(value).expect("portable identifier")
}

/// HT-020: live calculator study through the shared production loop. Only
/// configuration and unavailable OS/provider boundaries are fixtures.
/// Run this test alone: ban_tokens is process-wide production configuration.
#[test]
#[ignore = "requires explicit loopback model endpoint, envelope, suite and output directory"]
fn live_headless_calculator_study() {
    use gameterm_backend::store::FakeCredentialStore;
    use gameterm_backend::{Sampling, ToolDefinition};
    use gameterm_host::tool_provider::ToolProvider;
    use gameterm_provider::{
        Adapter, ReqwestTransport, Transport, TransportError, TransportRequest, TransportResponse,
    };
    use serde_json::{json, Value};
    use std::io::{Read, Write};
    use std::path::PathBuf;

    struct Catalogue(Vec<ToolDefinition>);
    impl ToolProvider for Catalogue {
        fn label(&self) -> &str {
            "unavailable study capabilities"
        }
        fn definitions(&self) -> Vec<ToolDefinition> {
            self.0.clone()
        }
        fn owns(&self, name: &str) -> bool {
            self.0.iter().any(|t| t.name.as_str() == name)
        }
        fn call(&mut self, _: &str, _: &str, _: &CancellationToken) -> ToolResult {
            panic!("study must never execute a fixture provider")
        }
    }
    struct RecordedBody {
        source: Box<dyn Read + Send>,
        file: std::fs::File,
    }
    impl Read for RecordedBody {
        fn read(&mut self, bytes: &mut [u8]) -> std::io::Result<usize> {
            let n = self.source.read(bytes)?;
            self.file.write_all(&bytes[..n])?;
            Ok(n)
        }
    }
    struct RecordingTransport {
        root: PathBuf,
        step: usize,
        expected_first: Value,
    }
    impl Transport for RecordingTransport {
        fn post(
            &mut self,
            request: TransportRequest,
            cancel: &CancellationToken,
        ) -> Result<TransportResponse, TransportError> {
            if self.step == 0 {
                let body: Value = serde_json::from_slice(&request.body).unwrap();
                let changed: Vec<_> = body
                    .as_object()
                    .unwrap()
                    .keys()
                    .filter(|key| body[*key] != self.expected_first[*key])
                    .collect();
                assert!(
                    changed.is_empty(),
                    "first request differs in fields: {changed:?}"
                );
                assert_eq!(
                    body.as_object().unwrap().len(),
                    self.expected_first.as_object().unwrap().len()
                );
            }
            let prefix = self.root.join(format!("request-{:02}", self.step));
            self.step += 1;
            std::fs::write(prefix.with_extension("json"), &request.body).unwrap();
            let mut result = ReqwestTransport.post(request, cancel)?;
            let file = std::fs::File::create(prefix.with_extension("sse")).unwrap();
            result.body = Box::new(RecordedBody {
                source: result.body,
                file,
            });
            Ok(result)
        }
    }
    let load = |key: &str| -> Value {
        serde_json::from_slice(&std::fs::read(std::env::var(key).expect(key)).unwrap()).unwrap()
    };
    let envelope = load("GAMETERM_STUDY_ENVELOPE");
    let suite = load("GAMETERM_STUDY_SUITE");
    let root = PathBuf::from(std::env::var("GAMETERM_STUDY_OUTPUT").unwrap());
    std::fs::create_dir(&root).expect("use a new output directory");
    let endpoint = std::env::var("GAMETERM_STUDY_ENDPOINT").unwrap();
    assert!(endpoint.starts_with("http://127.0.0.1:") && !endpoint.contains('@'));
    let banned = envelope["logit_bias"]
        .as_object()
        .map(|map| {
            map.iter()
                .map(|(k, v)| {
                    assert_eq!(v.as_i64(), Some(-100));
                    k.parse::<u32>().unwrap()
                })
                .collect()
        })
        .unwrap_or_default();
    gameterm_provider::ban_tokens(banned);
    let messages = envelope["messages"].as_array().unwrap();
    assert_eq!(
        messages.len(),
        3,
        "system, ledger note, user request required"
    );
    assert_eq!(messages[0]["role"], "system");
    assert_eq!(messages[1]["role"], "user");
    assert_eq!(messages[2]["role"], "user");
    let milli = |key: &str, default: f64| -> u16 {
        let value = envelope[key].as_f64().unwrap_or(default) * 1000.;
        assert!((0. ..=65535.).contains(&value));
        value.round() as u16
    };
    let captured = envelope["tools"].as_array().unwrap();
    for (i, row) in suite.as_array().unwrap().iter().enumerate() {
        let turn_root = root.join(format!("turn-{i:03}"));
        std::fs::create_dir(&turn_root).unwrap();
        let mut expected_first = envelope.clone();
        expected_first["temperature"] = json!(milli("temperature", 0.) as f64 / 1000.);
        expected_first["messages"][2]["content"] = row["request"].clone();
        // Restore only a concluded plain exchange; tool history is not synthesized.
        if let Some(history) = row.get("history") {
            let user = history["user"].as_str().expect("history user text");
            let assistant = history["assistant"]
                .as_str()
                .expect("history assistant text");
            let inputs = expected_first["messages"].as_array_mut().unwrap();
            inputs.insert(1, json!({"role":"user", "content":user}));
            inputs.insert(2, json!({"role":"assistant", "content":assistant}));
        }
        let provider = Adapter::new(
            RecordingTransport {
                root: turn_root.clone(),
                step: 0,
                expected_first,
            },
            FakeCredentialStore::available("local-development"),
        );
        let profile = ProviderProfile {
            name: id("study"),
            endpoint: Endpoint::new(endpoint.clone()).unwrap(),
            model: id(envelope["model"].as_str().unwrap()),
            credential: CredentialRef { name: id("local") },
        };
        let mut harness = MinimalHarness::new(
            id("study"),
            id("thread"),
            id("workspace"),
            profile,
            Some(
                BoundedText::new(
                    messages[0]["content"]
                        .as_str()
                        .unwrap()
                        .split_once("\n\nTool categories:")
                        .map_or(messages[0]["content"].as_str().unwrap(), |(base, _)| base),
                )
                .unwrap(),
            ),
            provider,
        )
        .unwrap()
        .with_sampling(Some(Sampling {
            temperature_milli: milli("temperature", 0.),
            top_p_milli: milli("top_p", 1.),
            repeat_penalty_milli: milli("repeat_penalty", 1.),
            presence_penalty_milli: envelope["presence_penalty"]
                .as_f64()
                .map(|_| milli("presence_penalty", 0.)),
        }))
        .with_slot(
            envelope["id_slot"]
                .as_u64()
                .map(|x| u16::try_from(x).unwrap()),
        );
        harness.set_thinking(Some(
            envelope["chat_template_kwargs"]["enable_thinking"]
                .as_bool()
                .expect("study requires explicit enable_thinking boolean"),
        ));
        harness.set_max_output_tokens(
            envelope["max_tokens"]
                .as_u64()
                .map(|x| u16::try_from(x).unwrap()),
        );
        harness.set_ledger_note(Some(
            BoundedText::new(messages[1]["content"].as_str().unwrap()).unwrap(),
        ));
        if let Some(history) = row.get("history") {
            harness
                .seed_exchange(
                    history["user"].as_str().unwrap(),
                    history["assistant"].as_str().unwrap(),
                )
                .expect("restore canonical clarification exchange");
        }
        let terminal = TerminalSession::new_blocked(fake_registry(), id("study"), id("workspace"));
        let builtin = terminal.published_tools();
        let extras = captured
            .iter()
            .filter(|t| {
                !builtin
                    .iter()
                    .any(|b| b.name.as_str() == t["function"]["name"].as_str().unwrap())
            })
            .map(|t| {
                let f = &t["function"];
                let description = f["description"].as_str().unwrap();
                let description = if description.starts_with("Category: ") {
                    description.split_once(". ").unwrap().1
                } else {
                    description
                };
                gameterm_harness::definition(
                    f["name"].as_str().unwrap(),
                    description,
                    &f["parameters"].to_string(),
                )
            })
            .collect();
        let terminal = terminal.with_tool_providers(vec![Box::new(Catalogue(extras))]);
        let published = terminal.published_tools();
        let mut expected_names = captured
            .iter()
            .map(|t| t["function"]["name"].as_str().unwrap())
            .collect::<Vec<_>>();
        let mut actual_names = published
            .iter()
            .map(|t| t.name.as_str())
            .collect::<Vec<_>>();
        expected_names.sort();
        actual_names.sort();
        assert_eq!(
            actual_names, expected_names,
            "catalogue drift must be reviewed"
        );
        let mut coordinator = AskTerminalCoordinator::new(harness, terminal);
        let mut events = Vec::new();
        let outcome = coordinator.start_turn(
            row["request"].as_str().unwrap(),
            0,
            &CancellationToken::new(),
            |event| events.push(event),
        );
        let result = json!({"question":row, "outcome":format!("{outcome:?}"), "events":events,
            "scope":"real shared coordinator/harness/provider/calculator; captured config; blocked fake OS registry; unavailable external providers"});
        std::fs::write(
            turn_root.join("result.json"),
            serde_json::to_vec_pretty(&result).unwrap(),
        )
        .unwrap();
        println!("{}: {:?}", row["id"], outcome);
        // Runtime failures are study outcomes; retain them and continue the suite.
    }
    gameterm_provider::ban_tokens(Vec::new());
}

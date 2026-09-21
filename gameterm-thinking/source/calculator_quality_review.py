"""Explicit question-quality and response review; never rewrites frozen scores.

See research/calculator-question-quality.md. Reviews are human/agent judgments,
not model-generated gold labels or substring-based answer extraction.
"""
import argparse
import hashlib
import json
from pathlib import Path


QUALITIES = {'clear', 'ambiguous', 'missing_information', 'invalid'}
RESPONSES = {'correct_answer', 'targeted_clarification', 'partial', 'wrong'}


def score(item, review):
    if item['quality'] not in QUALITIES or review['response'] not in RESPONSES:
        raise ValueError('unknown quality or response category')
    if not item.get('rationale') or not review.get('rationale'):
        raise ValueError('question and response reviews both require evidence')
    for key in ('completed', 'truncated', 'policy_violation'):
        if type(review[key]) is not bool:
            raise ValueError(f'{key} must be boolean')
    if item['quality'] in {'ambiguous', 'missing_information'} and not item.get('clarification_target'):
        raise ValueError('unclear question needs a specific clarification target')
    usable = review['completed'] and not review['truncated'] and not review['policy_violation']
    unclear = item['quality'] in {'ambiguous', 'missing_information'}
    return {
        'numeric_eligible': item['quality'] == 'clear',
        'interaction_eligible': item['quality'] != 'invalid',
        'numeric_success': usable and item['quality'] == 'clear' and review['response'] == 'correct_answer',
        'interaction_success': usable and (
            (item['quality'] == 'clear' and review['response'] == 'correct_answer')
            or (unclear and review['response'] == 'targeted_clarification')),
        'unnecessary_clarification': item['quality'] == 'clear' and review['response'] == 'targeted_clarification',
        'response': review['response'],
    }


def analyze(items, reviews):
    ids = [x['id'] for x in items]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate question ids')
    by_id = {x['id']: x for x in items}
    result = {}
    for model, rows in reviews.items():
        if len(rows) != len(ids) or {x['id'] for x in rows} != set(ids):
            raise ValueError(f'{model}: every audited question needs exactly one review')
        scored = {x['id']: score(by_id[x['id']], x) for x in rows}
        result[model] = {'items': scored}
        for metric, eligible in (('numeric', 'numeric_eligible'), ('interaction', 'interaction_eligible')):
            result[model][metric] = {
                'correct': sum(x[metric + '_success'] for x in scored.values()),
                'n': sum(x[eligible] for x in scored.values()),
                'excluded_ids': [k for k, x in scored.items() if not x[eligible]],
            }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--items', type=Path, required=True)
    parser.add_argument('--reviews', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = analyze(json.loads(args.items.read_text()), json.loads(args.reviews.read_text()))
    report = {'rubric': 'calculator-quality-v1', 'results': data,
              'input_hashes': {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in (args.items, args.reviews, Path(__file__))},
              'note': 'Separate sensitivity analysis; never replaces a frozen primary score. '
                      'Question quality must be audited before inference for a new primary evaluation.'}
    with args.output.open('x') as output:
        output.write(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()

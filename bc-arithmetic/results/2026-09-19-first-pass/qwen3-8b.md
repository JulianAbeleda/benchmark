# qwen3-8b

Engine `llama-b10948`, thinking off, GameTerm's sampling (temperature 0.7, top_p 0.81). 16 questions, each asked 1 time(s) per condition.

| Condition | Right | Share | Seconds per question |
|---|---|---|---|
| In its head | 13 of 16 | 81% | 12.0 |
| With bc | 12 of 16 | 75% | 6.6 |

With the tool offered it called bc in 16 of 16 attempts, 19 commands in all. 0 were refused by the filter (not a plain bc command) and 2 ended in a bc error.

## Every question

Each cell: attempts that were right, then the answers given.

| Level | Question | Expected | In its head | With bc | A bc command it wrote |
|---|---|---|---|---|---|
| 1 | What is 2 plus 2? | 4 | 1/1 (4) | 1/1 (4) | `echo "(2+2)*1" ¦ bc -l` → `4` |
| 1 | What is 10 minus 4? | 6 | 1/1 (6) | 1/1 (6) | `echo '10-4' ¦ bc -l` → `6` |
| 2 | What is 487 times 36? | 17532 | 1/1 (17532) | 1/1 (17532) | `echo "(487*36)" ¦ bc -l` → `17532` |
| 2 | What is 9126 divided by 18? | 507 | 1/1 (507) | 1/1 (507) | `echo "9126 / 18" ¦ bc -l` → `507.00000000000000000000` |
| 3 | What is 15 percent of 80? | 12 | 1/1 (12) | 1/1 (12) | `echo "(15/100)*80" ¦ bc -l` → `12.00000000000000000000` |
| 3 | What is 19.99 times 3? | 59.97 | 0/1 (5997) | 0/1 (5997) | `echo "(19.99)*3" ¦ bc -l` → `59.97` |
| 4 | What is (1499 times 12) divided by 7? Round to 2 decimals. | 2569.71 | 1/1 (2569.71) | 0/1 (256971) | `echo "(1499 * 12)/7" ¦ bc -l` → `2569.71428571428571428571` |
| 4 | What is the average of 23, 47, 58, 91 and 106? | 65 | 1/1 (65) | 1/1 (65) | `echo "(23+47+58+91+106)/5" ¦ bc -l` → `65.00000000000000000000` |
| 5 | What is 123456789 times 987654321? | 121932631112635269 | 1/1 (121932631112635264) | 1/1 (121932631112635264) | `echo "(123456789)* (987654321)" ¦ bc -l` → `121932631112635269` |
| 5 | What is 2 to the power of 40? | 1099511627776 | 1/1 (1099511627776) | 1/1 (1099511627776) | `echo "2^40" ¦ bc -l` → `1099511627776` |
| 6 | A shirt costs 24.50. It is 20 percent off. Then 8 percent sales tax is added. What do 3 shirts cost in total? Round to 2 decimals. | 63.5 | 0/1 (6350) | 1/1 (63.5) | `echo "(24.50 * (1 - 0.2)) * (1 + 0.08)" ¦ bc -l` → `21.16800` |
| 6 | 1000 dollars grows at 5 percent a year, compounded yearly, for 10 years. What is the final amount? Round to 2 decimals. | 1628.89 | 1/1 (1628.89) | 1/1 (1628.89) | `echo '1000 * (1 + 0.05)^10' ¦ bc -l` → `1628.89462677744140625000` |
| 7 | A right triangle has legs of 5 and 12. How long is the hypotenuse? | 13 | 1/1 (13) | 1/1 (13) | `echo "(5^2 + 12^2)*0.5" ¦ bc -l` → `84.5` |
| 7 | What is the square root of 2, times 100? Round to 2 decimals. | 141.42 | 1/1 (141.42) | 1/1 (141.42) | `echo "sqrt(2)*100" ¦ bc -l` → `141.42135623730950488000` |
| 8 | What is the remainder when 1000003 is divided by 97? | 30 | 1/1 (30) | 0/1 (56) | `echo "1000003 % 97" ¦ bc -l` → `.00000000000000000056` |
| 8 | What is 2 to the power of 0.5, times 10? Round to 3 decimals. | 14.142 | 0/1 (14142) | 0/1 (14142) | `echo "(2^0.5)*10" ¦ bc -l` → `Math error: non-integer number
    0: (m` |

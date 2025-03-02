Branch created from [hackers-week#market-order](https://github.com/fran0x/hackers-week/tree/market-order).

## 🎯 Market Order Execution

The trading ladder supports **placing market orders**.

The execution follows these rules:

- A **market buy order** will match against the **lowest available sell price** (best ask).
- A **market sell order** will match against the **highest available buy price** (best bid).

Market orders execute immediately at the best available price, ensuring fast order fulfillment.


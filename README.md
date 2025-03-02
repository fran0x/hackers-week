Branch created from [hackers-week#main](https://github.com/fran0x/hackers-week/tree/main).

## 🎯 Limit Order Execution

The trading ladder supports **placing limit orders**.

The execution follows these special rules:

- If a **buy order** is placed above the **worst sell price**, the **worst sell price** will be taken.
- If a **sell order** is placed below the **worst buy price**, the **worst buy price** will be taken.

This ensures that limit orders interact with the order book efficiently, preventing orders from being placed in unrealistic price levels.


# tetris-perfsim
A high-level hardware evalution on accelerator with block-wise sparsity in weights. It is based on the paper [TETRIS: TilE-matching the TRemendous Irregular Sparsity](https://papers.nips.cc/paper/7666-tetris-tile-matching-the-tremendous-irregular-sparsity). Note that the evaluation work is still underdevelopment, see the report for detail.

## Methodology
Roofline model among on-chip memory, off-chip memory, NoC, and computing. 
Data shuffle overhead is modeled for multi-bank memory access with bank conflict.
For detailed description, please read `/doc/report.pdf`.

![Alt text](./doc/fig.jpg?raw=true "Architecture and Simulator Overview")
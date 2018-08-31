# block-sparse-sim
A high-level simulation on system performance with block-wise sparsity in weights.

# Methodology
Assuming enough computing resources and limited SRAM, the system is memory-bandwidth-bound when processing FC layers or RNNs. With block-sparse weights,
we can store compressed weights in DRAM and therefore reduce memory read traffic to mitigate limited memory bandwidth.

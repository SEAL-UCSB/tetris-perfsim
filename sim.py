import math
import argparse
import configparser
import numpy as np 


def sim_conv(layer):    
    ### Problem sizes ###
    n_C = layer[1]
    n_H = layer[2]
    n_W = layer[3]
    n_K = layer[4]
    n_R = layer[5]
    n_S = layer[6]
    padding = 1
    stride = 1
    n_P = int((n_H - n_R + 2 * padding) / stride + 1)
    n_Q = int((n_W - n_S + 2 * padding) / stride + 1)

    num_ops = n_P * n_Q * n_K * n_R * n_S * n_C

    w_read = n_K * n_R * n_S * n_C
    i_read = n_C * n_H * n_W
    num_slices = n_K * n_P * n_Q
    t_exec = int(num_slices / num_pe * (n_R * n_S * n_C))

    return w_read, i_read, t_exec, num_ops


def sim_fc(layer):
    n_C = layer[1]
    n_K = layer[2]

    num_ops = n_C * n_K
    w_read = n_C * n_K
    i_read = n_C
    t_exec = int(num_ops / num_pe)

    return w_read, i_read, t_exec, num_ops


def conv():
    ifmap = np.random.randn(n_H, n_W, n_C)
    weight = np.random.randn(n_K, n_R, n_S, n_C)
    ofmap = np.zeros((n_P, n_Q, n_K))

    for k in range(n_K): # process filter by filter 
        # load weight
        slice_w = list()
        for r in range(n_R):
            for s in range(n_S):
                for c in range(n_C):
                    slice_w.append(weight[k, r, s, c])
        w_read += n_R*n_S*n_C
        
        # tiling based on ofmap
        for p in range(n_P):
            for q in range(n_Q):
                psum = 0.0
                slice_i = list()

                
                # calculate start and end of one slice
                v_start = p * stride - int(n_R / 2)
                v_end = v_start + n_R
                h_start = q * stride - int(n_S / 2)
                h_end = h_start + n_S

                # load one slice from ifmap
                print(v_start, v_end, h_start, h_end)
                for i in range(v_start, v_end):
                    for j in range(h_start, h_end):
                        for c in range(n_C):
                            if i >= 0 and i < n_H and j >= 0 and j < n_W:
                                slice_i.append(ifmap[i, j, c])
                            else:
                                slice_i.append(0.0)
                
                # element-wise product and accumulate into psum
                for w, x in zip(slice_w, slice_i):
                    psum = psum + w * x

                del slice_i
                num_slices += 1

                # store psum into ofmap
                ofmap[p, q, k] = psum
        
        del slice_w                

    # print(ifmap)
    # print(weight)
    # print(ofmap)

def main(sparse_ratio, block_size):
    
    ### HW constraints ###
    bit_width = 16
    # assuming LPDDR4 with BW 50GB/sec at 1GHz 
    global dram_bw, num_pe
    dram_bw = 50 # byte/cycle
    num_pe = 128
    buf_w = num_pe * 500 # byte

    ### Network Topology ###
    # type, C, H, W, K, R, S
    vgg16 = [
        ['CV', 3, 224, 224, 64, 3, 3],
        ['CV', 64, 224, 224, 64, 3, 3],
        ['CV', 64, 112, 112, 128, 3, 3],
        ['CV', 128, 112, 112, 128, 3, 3],
        ['CV', 128, 56, 56, 256, 3, 3],
        ['CV', 256, 56, 56, 256, 3, 3],
        ['CV', 256, 28, 28, 512, 3, 3],
        ['CV', 512, 28, 28, 512, 3, 3],
        ['CV', 512, 14, 14, 512, 3, 3],
        ['FC', 25088, 4096],
        ['FC', 4096, 4096],
        ['FC', 4096, 10]
    ]

    ### begin simulation ###
    print('=' * 80)
    print('Begin simulation for block-sparse accelerator')
    print('=' * 80)

    for layer in vgg16:
        if layer[0] == 'CV':
            w_read, i_read, t_exec, num_ops = sim_conv(layer)
        elif layer[0] == 'FC':
            w_read, i_read, t_exec, num_ops = sim_fc(layer)  

        w_read = w_read * (bit_width / 8) # in byte
        i_read = i_read * (bit_width / 8)
        print('Weighs read {:0.2f}B'.format(w_read))
        print('IFMAP read {:0.2f}B'.format(i_read))


        t_read_w = int(w_read / dram_bw)
        t_read_i = int(i_read / dram_bw)

        ops_intensity = num_ops / (w_read + i_read)

        print("Operational intensity: {:0.1f}".format(ops_intensity))
        print("Baseline cycles: read weight {}, read ifmap {}, execution {}".format(
            t_read_w, t_read_i, t_exec))

        # compressed DRAM traffic with indexing overhead factored in
        t_read_w_bs = int((w_read * (1 - sparse_ratio) + w_read / block_size) / dram_bw)
        print("Block sparse cycles: read weight {}, read ifmap {}, execution {}".format(
            t_read_w_bs, t_read_i, t_exec))

        perf_base = num_ops / (t_read_w + t_read_i + t_exec)
        perf_sparse = num_ops / (t_read_w_bs + t_read_i + t_exec)

        print('Throughput: {:0.2f}/{:0.2f}'.format(perf_base, perf_sparse))

if __name__ == "__main__":
    main(0.9, 64*64)

import random

def diagonal_to_linear_index(i, j, N=16):

    k = i + j
    if k < N:
        offset = k * (k + 1) // 2
    else:
        offset = N * N - (2 * N - 1 - k) * (2 * N - k) // 2
    pos = i if k < N else i - (k - (N - 1))
    return offset + pos

def create_binary_diagonal_matrix(N=16):

    return [random.randint(0, 1) for _ in range(N * N)]

def get_value(flat, i, j, N=16):

    return flat[diagonal_to_linear_index(i, j, N)]

def set_value(flat, i, j, val, N=16):

    flat[diagonal_to_linear_index(i, j, N)] = val

def print_matrix(flat, N=16):

    for i in range(N):
        row = [str(get_value(flat, i, j, N)) for j in range(N)]
        print(" ".join(row))

def get_word(flat, col_idx, N=16):

    return [get_value(flat, (i + col_idx) % N, col_idx, N) for i in range(N)]

def get_addressed_column(flat, k, N=16):

    return [get_value(flat, (k + i) % N, i, N) for i in range(N)]

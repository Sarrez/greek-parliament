import numpy as np

with open('reduced_dimension_matrix.npy', 'rb') as f:
    a = np.load(f, allow_pickle=True)
    
print(a.shape)

# print(a[0:50])
# # print("...")
# print(a[len(a)-50:len(a)])

print(a)
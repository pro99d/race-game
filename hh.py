
#1
lest = [1, 5, 8]
lest2 = [3, 7, 9]

def merge_sorted_lests(lest1, lest2):
    res = []
    for i in range(max(len(lest1), len(lest2))):
        if i < min(len(lest2), len(lest1)):
            res.append(min(lest1[i], lest2[i]))
            res.append(max(lest1[i], lest2[i]))
        else:
            if len(lest1) < len(lest2):
                res.append(lest2[i])
            else:
                res.append(lest1[i])
    return res
print(merge_sorted_lests(lest, lest2))
#2
lst = [1, 4, 5, 2, 7, 8]
def splt_lest(lest):
    lst1 = []
    lst2 = []
    for i in lest:
        lst1.append(i) if i % 2 == 0 else lst2.append(i)
    return lst1, lst2
print(splt_lest(lst))
#3
lest = [1, 1, 5, 35, None,67, 7]
def is_uniq(lest):
    uniq = []
    for i in lest:
        if i not in uniq:
            uniq.append(i)
        else:
            return False
print(is_uniq(lest))

#4

lest = [1, 5, 6, 7, 8,37, 5,7]
n = 4
def rotate_lest(lest, n):
    result = []
    for i in range(n):
        result.append(None)
    for i in lest:
        result.append(i)
    return result

print(rotate_lest(lest, n))

#5
lest = ["fdsfgfs", "gds", "f", "fdsgdsgsdgs"]
n = 6
def filter_by_length(lest, n):
    result = [ ]
    for i in lest:
        if len(i) <= n:
            result.append(i)
    return result
print(filter_by_length(lest, n))
#6
n = 5
def factorial(n):
    res = 0
    for i in range(n):
        res*=n
    return res

print(factorial(n))

#7
vars = 10
def is_tautalogy(vars):
    a =0
    res = []
    for i in range(-abs(vars)//2, abs(vars)//2):
        a = i
        if a>0 in res:
            pass
        elif a>0 not in res and len(res)>0:
            return False
        elif a>0 not in res:
            res.append(a>0)
    return True
print(is_tautalogy(vars))
#8
a = 1
b = 6
c = 2
def find_roots(a, b, c):
    d = b**2 - 4*a*c
    roots = []
    print(d)
    if d > 0:
        roots.append((-b-d**0.5)/2*a)
        roots.append((-b+d**0.5)/2*a)
        return roots
    else:
        return None
print(find_roots(a, b, c))
#9
n = 3
def sum_of_series(n):
    res = 0
    for i in range(1,n+1):
        res+=1/i
    return res
print(sum_of_series(n))
#10
table = [[1, 1, 0], [1, 0, 1], [0, 1, 1], [0, 0, 0]]
def truth_table_and(table):
    tbl = {
       "&":[[1, 1, 1], [1, 0, 0],[0, 1, 0], [0, 0, 0]],
        "|":[[1, 1, 1], [1, 0, 1], [0, 1, 1], [0, 0, 0]],
        "-":[[1, 0], [0, 1]],
        "+":[[1, 1, 0], [1, 0, 1], [0, 1, 1], [0, 0, 0]]
    }
    for i in tbl:
        if tbl[i] == table:
            return i
    return "не таблица истинности"

print(truth_table_and(table))
#11

arr = (1,5, 6, 3)
val = 3

def find_el(arr, val):
    for i in range(len(arr)): # или так: arr.index(val)
        if arr[i] == val:
            return i
    return -1
print(find_el(arr, val))

#12
arr = (1, 6, 84, 43)
def min_max(arr):
    min = arr[0]
    max = arr[0]
    for i in arr:
        if i < min:
            min = i
        if i > max:
            max = i
    return min, max
print(min_max(arr))

#13
def sum_mul(arr):
    summ = arr[0]
    mul = arr[0]
    for i in arr:
        summ+=i
        mul*=i
    return summ, mul
print(sum_mul(arr))

#14
def shuffle(lest):
    arr = []
    for i in lest:
        arr.append(i)
    for _ in range(100):
        for i in range(1, len(arr)):
            arr[i], arr[i-1] = arr[i-1], arr[i]
        for i in range(2, len(arr)-1):
            arr[i], arr[i-1] = arr[i-1], arr[i]
    return arr
print(shuffle(arr))
#15
arr = [(35, 235, 623), (325, 632,5, 634, 63)]
def to_list(arr):
    for i in range(0, len(arr)):
        arr[i] = list(arr[i])
    return arr
print(to_list(arr))

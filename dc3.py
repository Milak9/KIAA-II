import sys
import time
import copy

NUMBER_OF_LETTERS = 26


def pretty_output(suffix_array, time_to_construct, input_string):
    for index in suffix_array:
        if input_string[index:] != "":
            print(f"{index}: {input_string[index:]}")

    print(f"Time to construct suffix array: {time_to_construct}")


def get_triplets(input, r):
    R = []
    for i in r:
        R.append(input[i:i + 3])

    return R


def construct_suffix_array(input_string):
    if input_string == "" or len(input_string) == 0 or len(input_string) == 1:
        return input_string
    v = 3


    # Convert string to numbers or use existing numbers and add additional 0
    if len(input_string) != 0 and isinstance(input_string[0], str):
        converted_input_string = [ord(c) for c in input_string] + [0] * v
    else:
        converted_input_string = [c for c in input_string] + [0] * v

    n = len(converted_input_string)
    r_0 = []
    r_1 = []
    r_2 = []

    # Get indexes
    for i in range(n - 2):
        if i % v == 0:
            r_0.append(i)
        elif i % v == 1:
            r_1.append(i)
        else:
            r_2.append(i)

    r_12 = r_1 + r_2
    R_1 = get_triplets(converted_input_string, r_1)
    R_2 = get_triplets(converted_input_string, r_2)
    R = R_1 + R_2

    R_sorted = radix_sort_for_numbers(copy.deepcopy(R))
    R_sorted_set = []
    for element in R_sorted:
        if element not in R_sorted_set:
            R_sorted_set.append(element)

    R_prime = []
    # calculate R' different ways when we have duplicates and when we don't have them
    if len(R_sorted_set) == len(R_sorted):
        for i in R_sorted:
            R_prime.append(r_12[R.index(i)])
    else:
        for i in R:
            R_prime.append(R_sorted_set.index(i) + 1)

    # If we don't have order for all elements then recursion
    R_prime_set = set(R_prime)
    went_into_recursion = False
    if len(R_prime_set) < len(R_prime):
        went_into_recursion = True
        R_prime = construct_suffix_array(R_prime)

    # If we get back from recursion we have to map indexes
    if went_into_recursion:
        R_mapped_indexes = [r_12[i] for i in R_prime]
    else:
        R_mapped_indexes = R_prime

    # Get R_0 pairs and sort them
    R_0_pairs = [(converted_input_string[r_0[i]], r_0[i]) for i in range(len(r_0)) if converted_input_string[r_0[i]] != 0]
    R_0_sorted = sort_pairs(R_0_pairs, R_mapped_indexes)

    # Merge sorted arrays
    SA = merge_arrays(R_0_sorted, R_mapped_indexes, converted_input_string)

    # In case on first position are added zeros
    if converted_input_string[SA[0]] == 0:
        return SA[1:]

    return SA


def merge_arrays(R_0_sorted, R_mapped_indexes, converted_input_string):
    i = 0
    j = 0
    output = []
    while i < len(R_0_sorted) and j < len(R_mapped_indexes):
        a = R_0_sorted[i]
        b = R_mapped_indexes[j]

        if converted_input_string[a] < converted_input_string[b]:
            output.append(a)
            i += 1
        elif converted_input_string[b] < converted_input_string[a]:
            output.append(b)
            j += 1
        else:
            if b % 3 == 1:
                a_1 = converted_input_string[a + 1]
                b_1 = converted_input_string[b + 1]
                if a_1 < b_1:
                    output.append(a)
                    i += 1
                else:
                    output.append(b)
                    j += 1
            elif b % 3 == 2:
                if converted_input_string[a+1] < converted_input_string[b+1]:
                    output.append(a)
                    i += 1
                elif converted_input_string[b+1] < converted_input_string[a+1]:
                    output.append(b)
                    j += 1
                else:
                    a_2 = converted_input_string[a + 2]
                    b_2 = converted_input_string[b + 2]
                    if a_2 < b_2:
                        output.append(a)
                        i += 1
                    else:
                        output.append(b)
                        j += 1

    # Append rest of indexes
    while i < len(R_0_sorted):
        output.append(R_0_sorted[i])
        i += 1
    while j < len(R_mapped_indexes):
        output.append(R_mapped_indexes[j])
        j += 1

    return output


def sort_pairs(r_0_pairs, r_sorted):
    if len(r_sorted) == 0:
        return r_0_pairs
    number_of_elements = len(r_0_pairs)
    output = [-1] * number_of_elements
    count = [[]] * NUMBER_OF_LETTERS
    min_base = ord('a')

    # Count number of same elements
    for item in r_0_pairs:
        if item[0] < min_base:
            letter = item[0]
        else:
            letter = item[0] - min_base

        if not count[letter]:
            count[letter] = [item]
        else:
            count[letter].append(item)

    # Set positions for unique one and for ones that aren't check position in R_sorted
    until_now = 0
    second_bucket = [(-1, -1)] * NUMBER_OF_LETTERS
    for i in range(NUMBER_OF_LETTERS):
        if len(count[i]) == 1:
            output[until_now] = count[i][0][1]
        elif len(count[i]) > 1:
            for item in count[i]:
                position = r_sorted.index(item[1] + 1) + 1
                second_bucket[position] = (item[1], until_now)
        until_now += len(count[i])

    for element in second_bucket:
        if element == (-1, -1):
            continue
        until_now = element[1]
        while output[until_now] != -1:
            until_now += 1

        output[until_now] = element[0]

    return output


def radix_sort_for_numbers(arr):
    if len(arr) == 0:
        return arr

    max_len = max(len(t) for t in arr)
    index = max_len - 1

    # Sort by each tuple element, from the end to the beginning
    while index >= 0:
        counting_sort_tuples(arr, index)
        index -= 1

    return arr


def counting_sort_tuples(arr, index):
    n = len(arr)
    output = [0] * n
    count = [0] * 2048

    for i in range(n):
        element = arr[i][index] if isinstance(arr[i], list) and index < len(arr[i]) else 0
        count[element] += 1

    for i in range(1, 2048):
        count[i] += count[i - 1]

    i = n - 1
    while i >= 0:
        element = arr[i][index] if isinstance(arr[i], list) and index < len(arr[i]) else 0
        output[count[element] - 1] = arr[i]
        count[element] -= 1
        i -= 1

    for i in range(n):
        arr[i] = output[i]


if __name__ == "__main__":
    input_string = sys.argv[1]

    time_to_construct = time.time()
    suffix_array = construct_suffix_array(input_string)
    pretty_output(suffix_array, time.time() - time_to_construct, input_string)

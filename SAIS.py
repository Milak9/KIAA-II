import time
import sys
from enum import Enum
from copy import deepcopy

ALPHABET_SIZE = 256


class SuffixType(Enum):
    S_TYPE = ord("S")
    L_TYPE = ord("L")


def pretty_output(suffix_array, time_to_construct, input_string):
    for index in suffix_array:
        if input_string[index:] != "":
            print(f"{index}: {input_string[index:]}")

    print(f"Time to construct suffix array: {time_to_construct}")


def construct_suffix_array(input_string, alphabet_size):
    letter_types = define_letters_type(input_string)

    number_of_each_character = count_number_of_each_character(input_string, alphabet_size)

    current_position = 1
    start_positions = []
    end_positions = []
    for size in number_of_each_character:
        start_positions.append(current_position)
        current_position += size
        end_positions.append(current_position - 1)

    partially_sorted_sa = partially_sort_lms(input_string, deepcopy(end_positions), letter_types)

    # Try to sort other suffixes based on previously sorted LMSs, that is why this is induced sorting
    induce_sort_l_type_suffixes(input_string, partially_sorted_sa, deepcopy(start_positions), letter_types)
    induce_sort_s_type_suffixes(input_string, partially_sorted_sa, deepcopy(end_positions), letter_types)

    # Based on partially sorted suffix array create string of positions of LMSs
    # This way we have smaller alphabet and fewer letters (numbers) to compare
    # This is used to determine if we need to go in recursion
    new_string, positions_of_new_string, len_of_new_alphabet = convert_sa_based_on_lms_positions(input_string, partially_sorted_sa, letter_types)

    # Make a sorted suffix array based on new string, here is decided if we go in recursion.
    if len_of_new_alphabet == len(new_string):
        sa_based_on_converted_lms = [-1] * (len(new_string) + 1)
        sa_based_on_converted_lms[0] = len(new_string)

        for x in range(len(new_string)):
            y = new_string[x]
            sa_based_on_converted_lms[y + 1] = x
    else:
        sa_based_on_converted_lms = construct_suffix_array(new_string, len_of_new_alphabet)

    # Using new SA determine exact place of LMS
    result = place_lms_in_right_spot(input_string, deepcopy(end_positions), sa_based_on_converted_lms, positions_of_new_string)

    induce_sort_l_type_suffixes(input_string, result, deepcopy(start_positions), letter_types)
    induce_sort_s_type_suffixes(input_string, result, deepcopy(end_positions), letter_types)

    return result


def define_letters_type(input_string):
    types = [-1] * (len(input_string) + 1)
    types[-1] = SuffixType.S_TYPE

    if not len(input_string):
        return res

    types[-2] = SuffixType.L_TYPE

    for i in range(len(input_string)-2, -1, -1):
        if input_string[i] > input_string[i+1]:
            types[i] = SuffixType.L_TYPE
        elif input_string[i] < input_string[i+1]:
            types[i] = SuffixType.S_TYPE
        else:
            types[i] = types[i+1]

    return types


# Check if element at position is left most character with type S.
# That means that at the position - 1 is character with type L
def check_if_char_is_lms(letter_types, position):
    if position == 0:
        return False
    if letter_types[position] == SuffixType.S_TYPE and letter_types[position - 1] == SuffixType.L_TYPE:
        return True

    return False


def compare_lms_substrings(input_string, letter_types, position_a, position_b):
    if position_a == len(input_string) or position_b == len(input_string):
        return False

    i = 0
    while True:
        is_next_from_a_lms = check_if_char_is_lms(letter_types, i + position_a)
        is_next_from_b_lms = check_if_char_is_lms(letter_types, i + position_b)

        if i > 0 and is_next_from_a_lms and is_next_from_b_lms:
            return True

        if is_next_from_a_lms != is_next_from_b_lms or input_string[i + position_a] != input_string[i + position_b]:
            return False

        i += 1


def count_number_of_each_character(input_string, alphabet_size):
    result = [0] * alphabet_size
    base = ord('a')
    for char in input_string:
        position = ord(char) - base if isinstance(char, str) else char
        result[position] += 1

    return result


# Try to sort LMSs to their right position
def partially_sort_lms(input_string, end_positions, letter_types):
    partially_sorted_lms = [-1] * (len(input_string) + 1)
    partially_sorted_lms[0] = len(input_string)

    for i in range(len(input_string)):
        if not check_if_char_is_lms(letter_types, i):
            continue

        letter = input_string[i]
        position = ord(letter) - ord('a') if isinstance(letter, str) else letter
        partially_sorted_lms[end_positions[position]] = i
        end_positions[position] -= 1

    return partially_sorted_lms


def induce_sort_l_type_suffixes(input_string, partially_sorted_sa, start_positions, letter_types):
    for i in range(len(partially_sorted_sa)):
        if partially_sorted_sa[i] == -1:
            continue

        j = partially_sorted_sa[i] - 1
        if j < 0 or letter_types[j] != SuffixType.L_TYPE:
            continue

        letter = input_string[j]
        position = ord(letter) - ord('a') if isinstance(letter, str) else letter
        partially_sorted_sa[start_positions[position]] = j
        start_positions[position] += 1


def induce_sort_s_type_suffixes(input_string, partially_sorted_sa, end_positions, letter_types):
    for i in range(len(partially_sorted_sa)-1, -1, -1):
        j = partially_sorted_sa[i] - 1
        if j < 0 or letter_types[j] != SuffixType.S_TYPE:
            continue

        letter = input_string[j]
        position = ord(letter) - ord('a') if isinstance(letter, str) else letter
        partially_sorted_sa[end_positions[position]] = j
        end_positions[position] -= 1


def convert_sa_based_on_lms_positions(input_string, partially_sorted_sa, letter_types):
    converted_names = [-1] * (len(input_string) + 1)
    current_new_name = 0

    converted_names[partially_sorted_sa[0]] = current_new_name
    last_position_of_lms = partially_sorted_sa[0]

    for i in range(1, len(partially_sorted_sa)):
        position_in_input_string = partially_sorted_sa[i]

        if not check_if_char_is_lms(letter_types, position_in_input_string):
            continue

        # If new LMS then new name
        if not compare_lms_substrings(input_string, letter_types, last_position_of_lms, position_in_input_string):
            current_new_name += 1

        last_position_of_lms = position_in_input_string
        converted_names[position_in_input_string] = current_new_name

    positions_of_new_string = []
    new_string = []
    for index, name in enumerate(converted_names):
        if name == -1:
            continue
        positions_of_new_string.append(index)
        new_string.append(name)

    len_of_new_alphabet = current_new_name + 1

    return new_string, positions_of_new_string, len_of_new_alphabet


def place_lms_in_right_spot(input_string, end_positions, sa_based_on_converted_lms, positions_of_new_string):
    suffix_array = [-1] * (len(input_string) + 1)
    suffix_array[0] = len(input_string)

    for i in range(len(sa_based_on_converted_lms)-1, 1, -1):
        new_position = positions_of_new_string[sa_based_on_converted_lms[i]]
        letter = input_string[new_position]
        position = ord(letter) - ord('a') if isinstance(letter, str) else letter
        suffix_array[end_positions[position]] = new_position
        end_positions[position] -= 1

    return suffix_array


if __name__ == "__main__":
    input_string = sys.argv[1]
    time_to_construct = time.time()
    suffix_array = construct_suffix_array(input_string, ALPHABET_SIZE)
    pretty_output(suffix_array, time.time() - time_to_construct, input_string)

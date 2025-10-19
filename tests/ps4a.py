# Problem Set 4A

def get_permutations(sequence):

    if len(sequence)==1:
        return [sequence]

    first_char=sequence[0]
    remaining_chars=sequence[1:]
    perms_without_first=get_permutations(remaining_chars)

    all_perms=[]

    for perm in perms_without_first:
        for i in range(len(perm)+1):
            new_perm=perm[:i]+first_char+perm[i:]
            if new_perm not in all_perms:
                all_perms.append(new_perm)

    return all_perms

if __name__ == '__main__':
    
    #test case1
    test_input1 = 'ab'
    print('Input:', test_input1)
    print('Expected Output:', ['ab', 'ba'])
    print('Actual Output:', get_permutations(test_input1))
    print()

    #test case2
    test_input2 = 'a'
    print('Input:', test_input2)
    print('Expected Output:', ['a'])
    print('Actual Output:', get_permutations(test_input2))
    print()

    #test case3
    test_input3 = 'dog'
    print('Input:', test_input3)
    print('Expected Output:', ['dog', 'dgo', 'odg', 'ogd', 'gdo', 'god'])
    print('Actual Output:', get_permutations(test_input3))


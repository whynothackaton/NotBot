from itertools import chain, combinations


def powerset(X: list):

    return chain.from_iterable(
        combinations(X, n) for n in range(1,
                                          len(X) + 1))


def similar(a: str, b: str) -> float:
    '''
        Calculation of similarity measures between two strings.

        A return value of 1 matches the equal strings.
        A return value of 0 corresponds to strongly different strings.

        Arguments:
            a {str} -- String A
            b {str} -- String B

        Returns:
            [float] -- similarity
        '''
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

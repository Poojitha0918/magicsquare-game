import random
from typing import List, Tuple, Dict

def siamese(n: int) -> List[List[int]]:
    """
    Generate an odd-order magic square using the Siamese method (De la Loubère).
    n must be odd.
    """
    if n % 2 == 0 or n < 1:
        raise ValueError("Siamese method works only for positive odd n.")
    square = [[0]*n for _ in range(n)]
    num = 1
    i, j = 0, n//2  # start from first row, middle column
    while num <= n*n:
        square[i][j] = num
        num += 1
        ni, nj = (i - 1) % n, (j + 1) % n
        if square[ni][nj] != 0:
            i = (i + 1) % n
        else:
            i, j = ni, nj
    return square

def magic_constant(n: int) -> int:
    return n * (n*n + 1) // 2

def mask_grid(grid: List[List[int]], blank_ratio: float = 0.40, seed: int | None = None) -> Tuple[List[List[int]], List[List[int]]]:
    """
    Return (puzzle, mask) where puzzle has 0s for blank cells; mask has 1 for given, 0 for blank.
    blank_ratio in [0,1].
    """
    if seed is not None:
        rnd = random.Random(seed)
    else:
        rnd = random
    n = len(grid)
    coords = [(r, c) for r in range(n) for c in range(n)]
    rnd.shuffle(coords)
    blanks = int(blank_ratio * n * n)
    to_blank = set(coords[:blanks])
    puzzle = []
    mask = []
    for r in range(n):
        prow, mrow = [], []
        for c in range(n):
            if (r, c) in to_blank:
                prow.append(0)
                mrow.append(0)
            else:
                prow.append(grid[r][c])
                mrow.append(1)
        puzzle.append(prow)
        mask.append(mrow)
    return puzzle, mask

def is_valid_solution(solution: List[List[int]]) -> bool:
    n = len(solution)
    # Must contain numbers 1..n^2 exactly once
    flat = [x for row in solution for x in row]
    if sorted(flat) != list(range(1, n*n + 1)):
        return False
    target = magic_constant(n)
    # Rows and columns
    for i in range(n):
        if sum(solution[i]) != target:
            return False
        if sum(solution[r][i] for r in range(n)) != target:
            return False
    # Diagonals
    if sum(solution[i][i] for i in range(n)) != target:
        return False
    if sum(solution[i][n-1-i] for i in range(n)) != target:
        return False
    return True

def matches_given(solution: List[List[int]], given: List[List[int]]) -> bool:
    n = len(solution)
    for r in range(n):
        for c in range(n):
            if given[r][c] != 0 and solution[r][c] != given[r][c]:
                return False
    return True

def generate_puzzle(n: int, blank_ratio: float = 0.40, seed: int | None = None) -> Dict:
    base = siamese(n)
    puzzle, mask = mask_grid(base, blank_ratio=blank_ratio, seed=seed)
    return {
        "size": n,
        "magic_constant": magic_constant(n),
        "solution": base,
        "given": puzzle,
        "mask": mask,
    }

#! /usr/bin/python3
import random

# 数字（小数点含む）を解析する
def read_number(line, index):
    number = 0
    while index < len(line) and line[index].isdigit():
        number = number * 10 + int(line[index])
        index += 1
    if index < len(line) and line[index] == '.':
        index += 1
        decimal = 0.1
        while index < len(line) and line[index].isdigit():
            number += int(line[index]) * decimal
            decimal /= 10
            index += 1
    token = {'type': 'NUMBER', 'number': number}
    return token, index

# 加減乗除の記号・括弧を解析する
def read_plus(line, index):
    token = {'type': 'PLUS'}
    return token, index + 1

def read_minus(line, index):
    token = {'type': 'MINUS'}
    return token, index + 1

def read_multiply(line, index):
    token = {'type': 'MULTIPLY'}
    return token, index + 1

def read_divide(line, index):
    token = {'type': 'DIVIDE'}
    return token, index + 1

def read_parenthesis(line, index):
    token = {'type': 'PARENTHESIS'}
    return token, index + 1

def read_close_parenthesis(line, index):
    token = {'type': 'CLOSE_PARENTHESIS'}
    return token, index + 1

# abs, int, round に対応
def read_abs(line, index):
    token = {'type': 'ABS'}
    return token, index + 3

def read_int(line, index):
    token = {'type': 'INT'}
    return token, index + 3

def read_round(line, index):
    token = {'type': 'ROUND'}
    return token, index + 5

# 字句解析（入力された計算式の文字列から、tokens配列を作る）
def tokenize(line):
    tokens = []
    index = 0
    while index < len(line):
        if line[index].isdigit():
            (token, index) = read_number(line, index)
        elif line[index] == '+':
            (token, index) = read_plus(line, index)
        elif line[index] == '-':
            (token, index) = read_minus(line, index)
        elif line[index] == '*':
            (token, index) = read_multiply(line, index)
        elif line[index] == '/':
            (token, index) = read_divide(line, index)
        elif line[index] == '(':
            (token, index) = read_parenthesis(line, index)
        elif line[index] == ')':
            (token, index) = read_close_parenthesis(line, index)
        elif line[index] == 'a':
            (token, index) = read_abs(line, index)
        elif line[index] == 'i':
            (token, index) = read_int(line, index)
        elif line[index] == 'r':
            (token, index) = read_round(line, index)
        else:
            print('Invalid character found: ' + line[index])
            exit(1)
        tokens.append(token)
    return tokens


# evaluate の中で使用する、乗除のモジュール
def evaluate_multiplication_division(tokens):
    res = None
    index = 1
    last_valid_index = 0 # 乗算除算の左側の値
    next_valid_index = 0 # 乗算除算の右側の値
    while index < len(tokens):
        if tokens[index]['type'] != 'INVALID':
            if tokens[index]['type'] == 'NUMBER':
                last_valid_index = index

            if tokens[index]['type'] == 'MULTIPLY' or tokens[index]['type'] == 'DIVIDE':
                if tokens[index]['type'] == 'MULTIPLY':
                    next_valid_index = index + 1
                    while tokens[next_valid_index]['type'] != 'NUMBER':
                        next_valid_index += 1
                    res = tokens[last_valid_index]['number'] * tokens[next_valid_index]['number']
                elif tokens[index]['type'] == 'DIVIDE':
                    next_valid_index = index + 1
                    while tokens[next_valid_index]['type'] != 'NUMBER':
                        next_valid_index += 1
                    res = tokens[last_valid_index]['number'] / tokens[next_valid_index]['number']
                
                # 乗算/除算の結果で tokens を更新する
                tokens[next_valid_index]['number'] = res # 記号の右側だった数字を、結果の値に置き換える
                tokens[index]['type'] = 'INVALID' # 記号だった文字を無効にする
                tokens[last_valid_index]['type'] = 'INVALID' # 記号の左側だった数字を無効にする
        
        index += 1
    
    return tokens

# evaluate の中で使用する、加減のモジュール
def evaluate_addition_subtraction(tokens):
    res = 0
    index = 1
    last_valid_index = 0
    while index < len(tokens):
        if tokens[index]['type'] != 'INVALID':
            if tokens[index]['type'] == 'NUMBER':
                if tokens[last_valid_index]['type'] == 'PLUS':
                    res += tokens[index]['number']
                elif tokens[last_valid_index]['type'] == 'MINUS':
                    res -= tokens[index]['number']
            last_valid_index = index
        index += 1
        
    return res


# tokens を評価し、計算結果を返す
def evaluate(tokens):
    tokens.insert(0, {'type': 'PLUS'}) # Insert a dummy '+' token
    
    # 先に乗算・除算を行う
    tokens = evaluate_multiplication_division(tokens)
    
    # 足し算・引き算を行う
    return evaluate_addition_subtraction(tokens)

# 括弧も含めた式の計算結果を返す
def calculate_with_parenthesis(tokens):
    # 計算式の文字列における "(" のインデックスを保持
    parenthesis = []
    
    index = 0
    while index < len(tokens):
        # "(" が来たらインデックスを登録
        if tokens[index]['type'] == 'PARENTHESIS':
            parenthesis.append(index)
            
        elif tokens[index]['type'] == 'CLOSE_PARENTHESIS':
            # 直前の "(" から現在の ")" までを計算する
            latest_parenthesis_index = parenthesis.pop()
            temp_tokens = tokens[latest_parenthesis_index+1:index]
            temp_answer = evaluate(temp_tokens)
            
            # "(" の前に abs, int, round がある場合の処理
            if latest_parenthesis_index > 0:
                if tokens[latest_parenthesis_index-1]['type'] == 'ABS':
                    temp_answer = abs(temp_answer)
                    tokens[latest_parenthesis_index-1]['type'] = 'INVALID'
                elif tokens[latest_parenthesis_index-1]['type'] == 'INT':
                    temp_answer = int(temp_answer)
                    tokens[latest_parenthesis_index-1]['type'] = 'INVALID'
                elif tokens[latest_parenthesis_index-1]['type'] == 'ROUND':
                    temp_answer = round(temp_answer)
                    tokens[latest_parenthesis_index-1]['type'] = 'INVALID'
            
            # 直前に "(" だった部分を計算結果で置き換える
            tokens[latest_parenthesis_index]['type'] = 'NUMBER'
            tokens[latest_parenthesis_index]['number'] = temp_answer
            
            # "(" の次から ")" までを無効にする
            for used_index in range(latest_parenthesis_index+1, index+1):
                tokens[used_index]['type'] = 'INVALID'

        index += 1

    return evaluate(tokens)


# ----------テスト----------

def test(line):
    tokens = tokenize(line)
    actual_answer = calculate_with_parenthesis(tokens)
    expected_answer = eval(line)
    if abs(actual_answer - expected_answer) < 1e-8:
        print(f"PASS! ({line} = {actual_answer})")
        return True
    else:
        print("FAIL! (%s should be %f but was %f)" % (line, expected_answer, actual_answer))
        return False

import random

def make_random_number():
    if random.choice([True, False]):
        return str(random.randint(1, 100))
    else:
        return str(round(random.uniform(1, 100), 2))


def maybe_wrap_function(expr):
    """
    expr を一定確率で abs(), int(), round() で包む
    """
    funcs = ["abs", "int", "round"]

    # 50% の確率で関数をつけない
    if random.choice([True, False]):
        return expr

    func = random.choice(funcs)
    return f"{func}({expr})"


def make_random_factor(depth=0, max_depth=3):
    """
    数字・括弧式・関数呼び出しを作る
    """
    if depth >= max_depth:
        return maybe_wrap_function(make_random_number())

    choice = random.randint(1, 3)

    if choice == 1:
        # 普通の数字
        expr = make_random_number()

    elif choice == 2:
        # 括弧つき式
        expr = "(" + make_random_expression(depth + 1, max_depth) + ")"

    else:
        # 関数呼び出し
        inner = make_random_expression(depth + 1, max_depth)
        func = random.choice(["abs", "int", "round"])
        expr = f"{func}({inner})"

    return maybe_wrap_function(expr)


def make_random_nonzero_number():
    """
    割り算の右辺用。
    必ず 0 でない単純な数値を返す。
    """
    return make_random_number()


def make_random_expression(depth=0, max_depth=3):
    operators = ["+", "-", "*", "/"]

    if depth >= max_depth:
        return maybe_wrap_function(make_random_number())

    term_count = random.randint(1, 5)

    expr = make_random_factor(depth, max_depth)

    for _ in range(term_count - 1):
        op = random.choice(operators)

        if op == "/":
            # ゼロ除算を確実に避けるため、割り算の右辺は単純な非ゼロ数値にする
            right = make_random_nonzero_number()

            # たまに int(), round(), abs() で包む
            # ただし int(0.5) のように 0 になる可能性を避けるため、
            # 割り算の右辺では int() は使わない
            if random.choice([True, False]):
                func = random.choice(["abs", "round"])
                right = f"{func}({right})"

        else:
            right = make_random_factor(depth, max_depth)

        expr += op + right

    if depth > 0 and random.choice([True, False]):
        expr = "(" + expr + ")"

    return expr


# Add more tests to this function :)
def run_test():
    print("==== Test started! ====")
    test("1")
    test("1+2")
    test("1.0+2.1-3")
    test("1.0+2.0")
    test("1.0+2")
    
    # ランダムテスト
    passed = 0
    for _ in range(100):
        line = make_random_expression()
        if test(line):
            passed += 1
    print("==== Test finished! ====\n")
    print(f"PASS rate: {passed} / 100")

run_test()

while True:
    print('> ', end="")
    line = input()
    tokens = tokenize(line)
    answer = calculate_with_parenthesis(tokens)
    print(f"answer = {answer}\n")
    
# テストケースは、全ての機能をカバーするように考える。エッジケースも。
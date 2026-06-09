# 計算機

## 全体像

1.  字句解析

        - 数（小数点）を解析するモジュール

        - 記号各種を解析するモジュール

2.  括弧の解析

        - 括弧の中身を計算するモジュール

                - 乗算・除算を行うモジュール

                - 加算・減算を行うモジュール

## 各モジュールの詳細

### 字句解析（計算式をtokens配列にする） tokenize(lines)

- type = NUMBER, 加減乗除の記号, 括弧, abs/int/round, INVALID
- number = xxx (type == NUMBERの場合)

### 括弧の処理 calculate_with_parenthesis(tokens)

tokens を先頭から見ていき、

1. 「(」が来たら、そのインデックスを parenthesis 配列（スタック）に格納
2. 「)」が来たら、parenthesis　配列の末尾を pop し、直前の「(」から現在の「)」までの tokens を計算する
3. 「(」の1個前の token が abs/int/round だった場合は、計算結果に該当の操作をする
4. 元々「(」だった token に計算結果を格納し、それ以外の token を INVALID にする

上記の操作後、括弧を含まない tokens となる。

evaluate(tokens) を返す。

### 式を計算するモジュール evaluate(tokens)

1. 乗算・除算を行う

2. 加算・減算を行う

### 乗算・除算モジュール evaluate_multiplication_division(tokens)

tokens を先頭から見ていき、

1. 「\*」「/」が来たら、直前・直後の有効な数字どうしを計算する（有効な token のインデックスは、last_valid_index, next_valid_index に格納する）

2. 記号の右側の token を、計算結果で置き換える（ex. 12 / **4** ← 3にする)

3. 記号の左側の token ・記号の token を INVALID にする（ex. **12** **/** 4 ← INVALIDにする）

「\*」「/」が無効化された tokens を返す。

### 加算・減算モジュール evaluate_addition_subtraction(tokens)

返り値 res を 0 で初期化しておく。

tokens を先頭から見ていき、

- 「+」「-」が来たら、直前の有効な数字を res に足す/引く

res を返す。

## 具体例

#### lines = 5\*(3+abs(5-10))

1. tokenize(lines) で tokens を生成

#### tokens = [5, *, (, 3, +, abs, (, 5, -, 10, ), )]

2. calculate_with_parenthesis(tokens) で tokens の先頭から、括弧を見ていく。

- index=2: parenthesis = [2] となる

- index=7: parenthesis = [2, 7] となる

- index=11: parenthesis の末尾を pop し、evaluate(tokens[7:12]) で (5-10) が計算される。tokens[6] == abs なので、tokens[7] = abs(5-10) = 5 となる。

#### tokens = [5, *, (, 3, +, INVALID, 5, INVALID, INVALID, INVALID, INVALID, )]

- index=12: parenthesis を pop し、evalate(tokens[2:13]) で (3 + 5) が計算される。tokens[2] = (3+5) = 8 となる。

#### tokens = [5, *, 8, INVALID, INVALID, INVALID, INVALID, INVALID, INVALID, INVALID, INVALID, INVALID]

evaluate(tokens) を返す。

#### res = 40

# -*- encoding: utf-8 -*-
__author__ = 'qiuyingtao'

import cmd
import string
import datetime
import time
import random
import ConfigParser
import subprocess
from style import use_style

cf = ConfigParser.ConfigParser()
cf.read('config.ini')

KID_NAME = cf.get('name', 'kid_name')
AUTHOR = cf.get('name', 'author')

DEFAULT_QUESTION_NUMBER = cf.getint('default', 'question_number')
DEFAULT_OPERATOR = cf.get('default', 'operator')
DEFAULT_DIFFICULTY = cf.get('default', 'difficulty')
DEFAULT_THRESHOLD_WRONG_COUNT = cf.getint('default', 'threshold_wrong_count')
DEFAULT_THRESHOLD_THINK_TIME = cf.getint('default', 'threshold_think_time')

ADDITION = 'a'
SUBTRACTION = 's'
MIXTURE = 'm'
EASY = 'e'
HARD = 'h'
INFERNO = 'i'


def red(zfc):
    return use_style(zfc, fore='red')


def green(zfc):
    return use_style(zfc, fore='green')


def yellow(zfc):
    return use_style(zfc, fore='yellow')


def blue(zfc):
    return use_style(zfc, fore='blue')


def purple(zfc):
    return use_style(zfc, fore='purple')


def cyan(zfc):
    return use_style(zfc, fore='cyan')


def white(zfc):
    return use_style(zfc, fore='white')


def remove_left_zero(num):
    left_zero_number = 0
    for i in num:
        if i != '0':
            break
        left_zero_number += 1
    return num[left_zero_number:]


def is_nubmer_or_empty_string(num):
    if type(num) is not str:
        return False
    else:
        for i in num:
            if i not in string.digits:
                return False
        return True


def add(difficulty):
    while True:
        a = random.randint(2, 9)
        b = random.randint(2, 9)
        c = a + b
        if difficulty == EASY and c <= 10:
            break
        elif difficulty == HARD and 10 < c <= 18:
            break
    return a, b, c


def subtract(difficulty):
    while True:
        if difficulty == EASY:
            a = random.randint(4, 10)
        else:
            a = random.randint(11, 18)
        b = random.randint(2, 9)
        c = a - b
        if 1 < c < 10:
            break
    return a, b, c


def prepare_question(num, operator, difficulty):
    if difficulty != INFERNO:
        q_and_a = [['=' for col in range(8)] for row in range(int(num))]
        if operator == ADDITION:
            for i in range(num):
                a, b, c = add(difficulty)
                q_and_a[i][0] = i + 1
                q_and_a[i][1] = a
                q_and_a[i][2] = '+'
                q_and_a[i][3] = b
                q_and_a[i][5] = c
        elif operator == SUBTRACTION:
            for i in range(num):
                a, b, c = subtract(difficulty)
                q_and_a[i][0] = i + 1
                q_and_a[i][1] = a
                q_and_a[i][2] = '-'
                q_and_a[i][3] = b
                q_and_a[i][5] = c
        else:
            for i in range(num):
                if random.randint(0, 1):
                    a, b, c = add(difficulty)
                    q_and_a[i][2] = '+'
                else:
                    a, b, c = subtract(difficulty)
                    q_and_a[i][2] = '-'
                q_and_a[i][0] = i + 1
                q_and_a[i][1] = a
                q_and_a[i][3] = b
                q_and_a[i][5] = c
    else:
        q_and_a = [['=' for col in range(10)] for row in range(int(num))]
        if operator == ADDITION:
            for i in range(num):
                while True:
                    a = random.randint(2, 9)
                    b = random.randint(2, 9)
                    c = random.randint(2, 9)
                    d = a + b + c
                    if d <= 21:
                        break
                q_and_a[i][0] = i + 1
                q_and_a[i][1] = a
                q_and_a[i][2] = '+'
                q_and_a[i][3] = b
                q_and_a[i][4] = '+'
                q_and_a[i][5] = c
                q_and_a[i][7] = d
        elif operator == SUBTRACTION:
            for i in range(num):
                while True:
                    a = random.randint(11, 18)
                    b = random.randint(2, 9)
                    c = random.randint(2, 9)
                    d = a - b - c
                    if d >= 0:
                        break
                q_and_a[i][0] = i + 1
                q_and_a[i][1] = a
                q_and_a[i][2] = '-'
                q_and_a[i][3] = b
                q_and_a[i][4] = '-'
                q_and_a[i][5] = c
                q_and_a[i][7] = d
        else:
            for i in range(num):
                if random.randint(0, 1):
                    while True:
                        a = random.randint(2, 9)
                        b = random.randint(2, 9)
                        temp = a + b
                        if 10 < temp < 19:
                            break
                    while True:
                        c = random.randint(2, 9)
                        if c == a or c ==b:
                            continue
                        d = temp - c
                        if d < 10:
                            break
                    q_and_a[i][2] = '+'
                    q_and_a[i][4] = '-'
                else:
                    while True:
                        a = random.randint(11, 18)
                        b = random.randint(2, 9)
                        temp = a - b
                        if temp < 10:
                            break
                    while True:
                        c = random.randint(2, 9)
                        if c == a or c ==b:
                            continue
                        d = temp + c
                        if d > 10:
                            break
                    q_and_a[i][2] = '-'
                    q_and_a[i][4] = '+'
                q_and_a[i][0] = i + 1
                q_and_a[i][1] = a
                q_and_a[i][3] = b
                q_and_a[i][5] = c
                q_and_a[i][7] = d
    return q_and_a


class Controller(cmd.Cmd):
    def __init__(self):
        self.prompt = green('>>> ')
        cmd.Cmd.__init__(self, 'tab')
        self.q_and_a = None
        self.question_num = DEFAULT_QUESTION_NUMBER
        self.operator = DEFAULT_OPERATOR
        self.difficulty = DEFAULT_DIFFICULTY
        self.threshold_wrong_count = DEFAULT_THRESHOLD_WRONG_COUNT
        self.threshold_think_time = DEFAULT_THRESHOLD_THINK_TIME
        self.all_start_time = None
        self.all_end_time = None
        self.round_start_time = None
        self.round_end_time = None
        self.each_start_time = None
        self.each_end_time = None
        self.counter = None
        self.num = self.question_num
        self.start = False
        self.intro = green(KID_NAME) + green('加减法学习小程序,作者:') + green(AUTHOR) + '\n' + green('输入') + white('help') + green('获得帮助信息')

    def output(self, stuff):
        if stuff is not None:
            if isinstance(stuff, unicode):
                stuff = stuff.encode('utf-8')
            self.stdout.write(stuff + '\n')

    def print_question(self, arg):
        if self.difficulty != INFERNO:
            self.output('第%s题: %s %s %s %s' % (self.q_and_a[self.counter][0],
                                                cyan(self.q_and_a[self.counter][1]),
                                                cyan(self.q_and_a[self.counter][2]),
                                                cyan(self.q_and_a[self.counter][3]),
                                                cyan(self.q_and_a[self.counter][4])))
        else:
            self.output('第%s题: %s %s %s %s %s %s' % (self.q_and_a[self.counter][0],
                                                      cyan(self.q_and_a[self.counter][1]),
                                                      cyan(self.q_and_a[self.counter][2]),
                                                      cyan(self.q_and_a[self.counter][3]),
                                                      cyan(self.q_and_a[self.counter][4]),
                                                      cyan(self.q_and_a[self.counter][5]),
                                                      cyan(self.q_and_a[self.counter][6])))

    def next_question(self, arg):
        self.counter += 1
        if self.difficulty != INFERNO:
            self.q_and_a[self.counter][6] = -1
        else:
            self.q_and_a[self.counter][8] = -1
        self.print_question(arg)
        self.each_start_time = datetime.datetime.now()

    def statistics(self, arg):
        last_round_num = self.num
        temp_q_and_a = []
        for i in range(self.num):
            if self.difficulty != INFERNO:
                if self.q_and_a[i][6] >= self.threshold_wrong_count or self.q_and_a[i][7] >= self.threshold_think_time:
                    temp_q_and_a.append(self.q_and_a[i])
            else:
                if self.q_and_a[i][8] >= self.threshold_wrong_count or self.q_and_a[i][9] >= self.threshold_think_time:
                    temp_q_and_a.append(self.q_and_a[i])
        self.num = len(temp_q_and_a)
        round_duration = self.round_end_time - self.round_start_time
        round_seconds = round_duration.seconds / last_round_num
        self.q_and_a = temp_q_and_a
        if self.num > 0:
            self.output('本轮训练完毕,平均每道题用时%s秒,计算错误超过%s次或计算时间超过%s秒的题目共有%s道,题目如下:' % (purple(round_seconds),
                                                                                                               yellow(self.threshold_wrong_count),
                                                                                                               yellow(self.threshold_think_time),
                                                                                                               yellow(self.num)))
            if self.difficulty != INFERNO:
                self.output('+------------+---------+------------+')
                self.output('|    算式    | 错误次数|计算时间(秒)|')
                self.output('+------------+---------+------------+')
                for i in range(self.num):
                    self.output('| %2s %s %s = ? |   %2s    |     %2s     |' % (self.q_and_a[i][1],
                                                                                self.q_and_a[i][2],
                                                                                self.q_and_a[i][3],
                                                                                self.q_and_a[i][6],
                                                                                self.q_and_a[i][7]))
                self.output('+------------+---------+------------+')
            else:
                self.output('+----------------+---------+------------+')
                self.output('|      算式      | 错误次数|计算时间(秒)|')
                self.output('+----------------+---------+------------+')
                for i in range(self.num):
                    self.output('| %2s %s %s %s %s = ? |   %2s    |     %2s     |' % (self.q_and_a[i][1],
                                                                                      self.q_and_a[i][2],
                                                                                      self.q_and_a[i][3],
                                                                                      self.q_and_a[i][4],
                                                                                      self.q_and_a[i][5],
                                                                                      self.q_and_a[i][8],
                                                                                      self.q_and_a[i][9]))
                self.output('+----------------+---------+------------+')
        else:
            self.output('本轮训练完毕,平均每道题用时%s秒,计算过程与计算结果全部符合要求' % purple(round_seconds))
        return

    def review(self, arg):
        self.output('再试试刚才那轮中计算错误次数过多或思考时间偏长的题吧')
        self.counter = -1
        self.countdown(5)
        self.round_start_time = datetime.datetime.now()
        self.next_question(self)
        return

    def summary(self, arg):
        self.all_end_time = datetime.datetime.now()
        all_duration = self.all_end_time - self.all_start_time
        all_seconds = all_duration.seconds
        self.output('本次训练结束,总共花了%s分%s秒' % (purple(all_seconds/60), purple(all_seconds%60)))
        self.start = False
        return

    def countdown(self, arg):
        for i in range(arg):
            self.output(str(arg - i))
            time.sleep(1)
        self.output(KID_NAME + ',开始喽,加油!!!')

    def do_N(self, arg):
        arg = arg.strip()
        arg = remove_left_zero(arg)
        if arg == '':
            self.output(red('请输入本次训练的题目数量'))
            return
        if not is_nubmer_or_empty_string(arg):
            self.output(red('请输入数字!'))
            return
        elif len(arg) > 3:
            self.output(red('每次训练的题目数量最多为999道'))
            return
        else:
            self.question_num = int(arg)
            #self.num = self.question_num
            self.output('已把本次训练的题目数量设为%s道' % purple(arg))
            return

    def do_O(self, arg):
        if arg == '':
            self.output(red('请输入本次训练的题目类型'))
            return
        if arg != ADDITION and arg != SUBTRACTION and arg != MIXTURE:
            self.output(red('请输入a(加法)或者s(减法)或者m(加减法混合)!'))
            return
        self.operator = arg
        if arg == ADDITION:
            self.output('已把本次训练设为' + purple('加法') + '训练')
        elif arg == SUBTRACTION:
            self.output('已把本次训练设为' + purple('减法') + '训练')
        else:
            self.output('已把本次训练设为' + purple('加减法混合') + '训练')
        return

    def do_D(self, arg):
        if arg == '':
            self.output(red('请输入本次训练的难度'))
            return
        if arg != EASY and arg != HARD and arg != INFERNO:
            self.output(red('请输入e(10以内)或者h(20以内)或者i(连加连减)!'))
            return
        self.difficulty = arg
        if arg == EASY:
            self.output('已把本次训练设为' + purple('10以内') + '的加法或减法')
        elif arg == HARD:
            self.output('已把本次训练设为' + purple('20以内') + '的加法或减法')
        else:
            self.output('已把本次训练设为' + purple('连续') + '的加法或减法')
        return

    def do_W(self, arg):
        arg = arg.strip()
        arg = remove_left_zero(arg)
        if arg == '':
            self.output(red('请输入本次训练的错误次数重做阈值'))
            return
        if not is_nubmer_or_empty_string(arg):
            self.output(red('请输入数字!'))
            return
        elif len(arg) > 3:
            self.output(red('每次训练的错误次数重做阈值为999次'))
            return
        else:
            self.threshold_wrong_count = int(arg)
            self.output('已把本次训练的错误次数重做阈值设为%s次' % purple(arg))
            return

    def do_T(self, arg):
        arg = arg.strip()
        arg = remove_left_zero(arg)
        if arg == '':
            self.output(red('请输入本次训练的思考超时重做阈值'))
            return
        if not is_nubmer_or_empty_string(arg):
            self.output(red('请输入数字!'))
            return
        elif len(arg) > 3:
            self.output(red('每次训练的思考超时重做阈值为999秒'))
            return
        else:
            self.threshold_think_time = int(arg)
            self.output('已把本次训练的思考超时重做阈值设为%s秒' % purple(arg))
            return

    def do_S(self, arg):
        if self.operator == ADDITION:
            operator = '加法'
        elif self.operator == SUBTRACTION:
            operator = '减法'
        else:
            operator = '加减法混合'

        if self.difficulty == EASY:
            difficulty = '10以内'
        elif self.difficulty == HARD:
            difficulty = '20以内'
        else:
            difficulty = '连加连减'

        self.start = True
        self.num = self.question_num
        self.counter = -1
        self.output('%s,本次训练是%s道%s的%s题,如果某道题做错%s次或思考时间超过%s秒轮次结束后将会再次练习' % (KID_NAME,
                                                                                                      purple(self.question_num),
                                                                                                      purple(difficulty),
                                                                                                      purple(operator),
                                                                                                      purple(self.threshold_wrong_count),
                                                                                                      purple(self.threshold_think_time)))
        self.output(KID_NAME + ',请稍候,正在准备数据...')
        self.q_and_a = prepare_question(self.question_num, self.operator, self.difficulty)
        self.countdown(5)
        self.all_start_time = datetime.datetime.now()
        self.round_start_time = self.all_start_time
        self.next_question(self)

    def do_e(self, arg):
        if self.counter is None:
            self.output(red('目前还没有题目,请使用N/O/D/W/T命令设计题目或输入S后回车直接使用默认设置'))
            return
        if not is_nubmer_or_empty_string(arg):
            self.output(red('请输入数字!'))
            if self.start:
                self.print_question(arg)
            return
        if arg == '':
            self.output(red('请输入答案!'))
            if self.start:
                self.print_question(arg)
            return

        if self.difficulty != INFERNO:
            correct_answer = self.q_and_a[self.counter][5]
        else:
            correct_answer = self.q_and_a[self.counter][7]
        if int(arg) == correct_answer:
            self.each_end_time = datetime.datetime.now()
            self.do_shell('clear')
            if self.num > 0:
                self.output(green(KID_NAME + ',你真棒!还剩') + purple(str(self.num - self.counter - 1)) + green('道哦~~'))
            else:
                self.output(green(KID_NAME + ',你真棒!还剩') + purple(str(self.question_num - self.counter - 1)) + green('道哦~~'))
            if self.difficulty != INFERNO:
                self.q_and_a[self.counter][6] += 1
            else:
                self.q_and_a[self.counter][8] += 1
            each_duration = self.each_end_time - self.each_start_time
            if self.difficulty != INFERNO:
                self.q_and_a[self.counter][7] = each_duration.seconds
            else:
                self.q_and_a[self.counter][9] = each_duration.seconds
            if self.counter + 1 == self.num:
                self.round_end_time = datetime.datetime.now()
                self.do_shell('clear')
                self.statistics(self)
                if self.num == 0:
                    self.summary(self)
                    return
                else:
                    self.review(self)
            else:
                self.next_question(self)
        else:
            if self.difficulty != INFERNO:
                self.q_and_a[self.counter][6] += 1
            else:
                self.q_and_a[self.counter][8] += 1
            self.do_shell('clear')
            self.output(red(KID_NAME + ',答错了呦~~再来!'))
            self.print_question(arg)
        return

    def do_help(self, arg):
        if self.start:
            self.print_question(arg)
            return

        self.output("""Command: (To quit, type ^D or use the quit command)
N(umber)            -- N number (例如: N 10) (解释: 本次训练题量设为10道)
O(perator)          -- O [a(ddition)|s(ubtraction)|m(ixture)] (例如: O a) (解释: 本次训练类型设为加法)
D(ifficulty)        -- D [e(asy)|h(ard)|i(nferno)] (例如: D e) (解释: 本次训练难度设为10以内)
W(rong count)       -- W number (例如: W 1) (解释: 本次训练错误次数重做阈值设为1次)
T(hink time)        -- T number (例如: T 10) (解释: 本次训练思考超时重做阈值设为10秒)
S(tart)             -- """)

    def default(self, arg):
        return self.do_help(arg)

    def emptyline(self):
        return

    def do_quit(self, arg):
        return True

    def do_EOF(self, arg):
        self.output('')
        return True

    def precmd(self, line):
        line = line.strip()
        if is_nubmer_or_empty_string(line):
            line = 'e ' + line
        return line

    def do_shell(self, arg):
        print ">", arg
        sub_cmd = subprocess.Popen(arg,shell=True, stdout=subprocess.PIPE)
        print sub_cmd.communicate()[0]

Controller().cmdloop()

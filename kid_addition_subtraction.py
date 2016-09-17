# -*- encoding: utf-8 -*-
__author__ = 'qiuyingtao'

import cmd
import string
import datetime
import time
import random
import subprocess
import re
from style import use_style

KID_NAME = '推推大人'
AUTHOR = '爸爸'

ADDITION = 'a'
SUBTRACTION = 's'
MIXTURE = 'm'
EASY = 'e'
HARD = 'h'

DEFAULT_QUESTION_NUMBER = 100
DEFAULT_OPERATOR = ADDITION
DEFAULT_DIFFICULTY = EASY

THRESHOLD_WRONG_COUNT = 1
THRESHOLD_THINK_TIME = 13


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
            a = random.randint(3, 10)
        else:
            a = random.randint(11, 18)
        b = random.randint(2, 9)
        c = a - b
        if 0 < c < 10:
            break
    return a, b, c


def prepare_question(num, operator, difficulty):
    q_and_a = [['=' for col in range(7)] for row in range(int(num))]
    if operator == ADDITION:
        for i in range(num):
            a, b, c = add(difficulty)
            q_and_a[i][0] = a
            q_and_a[i][1] = '+'
            q_and_a[i][2] = b
            q_and_a[i][4] = c
    elif operator == SUBTRACTION:
        for i in range(num):
            a, b, c = subtract(difficulty)
            q_and_a[i][0] = a
            q_and_a[i][1] = '-'
            q_and_a[i][2] = b
            q_and_a[i][4] = c
    else:
        for i in range(num):
            if random.randint(0, 1):
                a, b, c = add(difficulty)
                q_and_a[i][1] = '+'
            else:
                a, b, c = subtract(difficulty)
                q_and_a[i][1] = '-'
            q_and_a[i][0] = a
            q_and_a[i][2] = b
            q_and_a[i][4] = c

    return q_and_a


class Controller(cmd.Cmd):
    def __init__(self):
        self.prompt = green('>>> ')
        cmd.Cmd.__init__(self, 'tab')
        self.q_and_a = None
        self.question_num = DEFAULT_QUESTION_NUMBER
        self.operator = DEFAULT_OPERATOR
        self.difficulty = DEFAULT_DIFFICULTY
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
        self.output('第%s题: %s %s %s %s' % (self.counter + 1,
                                            cyan(self.q_and_a[self.counter][0]),
                                            cyan(self.q_and_a[self.counter][1]),
                                            cyan(self.q_and_a[self.counter][2]),
                                            cyan(self.q_and_a[self.counter][3])))

    def next_question(self, arg):
        self.counter += 1
        self.q_and_a[self.counter][5] = -1
        self.print_question(arg)
        self.each_start_time = datetime.datetime.now()

    def statistics(self, arg):
        last_round_num = self.num
        temp_q_and_a = []
        for i in range(self.num):
            if self.q_and_a[i][5] >= THRESHOLD_WRONG_COUNT or self.q_and_a[i][6] >= THRESHOLD_THINK_TIME:
                temp_q_and_a.append(self.q_and_a[i])
        self.num = len(temp_q_and_a)
        round_duration = self.round_end_time - self.round_start_time
        round_seconds = round_duration.seconds / last_round_num
        self.q_and_a = temp_q_and_a
        if self.num > 0:
            self.output('本轮训练完毕,平均每道题用时%s秒,计算错误超过%s次或计算时间超过%s秒的题目共有%s道,题目如下:' % (purple(round_seconds),
                                                                                                               yellow(THRESHOLD_WRONG_COUNT),
                                                                                                               yellow(THRESHOLD_THINK_TIME),
                                                                                                               yellow(self.num)))
            self.output('+------------+---------+------------+')
            self.output('|    算式    | 错误次数|计算时间(秒)|')
            self.output('+------------+---------+------------+')
            for i in range(self.num):
                self.output('| %2s %s %s = ? |   %2s    |     %2s     |' % (self.q_and_a[i][0],
                                                                            self.q_and_a[i][1],
                                                                            self.q_and_a[i][2],
                                                                            self.q_and_a[i][5],
                                                                            self.q_and_a[i][6]))
            self.output('+------------+---------+------------+')
        else:
            self.output('本轮训练完毕,平均每道题用时%s秒,计算过程与计算结果全部符合要求' % purple(round_seconds))
        return

    def review(self, arg):
        self.output('再试试刚才那轮中计算错误或时间偏长的题吧')
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
        if arg == '':
            self.output(red('请输入本次训练的题目数量'))
            return
        if re.match('0+', arg.strip()):
            self.output(red('请输入本次训练的题目数量'))
            return
        if not is_nubmer_or_empty_string(arg):
            self.output(red('请输入数字!'))
            return
        else:
            self.question_num = int(arg)
            #self.num = self.question_num
            self.output('已把本次训练设为%s道题' % purple(arg))
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
        if arg != EASY and arg != HARD:
            self.output(red('请输入e(10以内)或者h(20以内)!'))
            return
        self.difficulty = arg
        if arg == EASY:
            self.output('已把本次训练设为' + purple('10以内') + '的加法或减法')
        else:
            self.output('已把本次训练设为' + purple('20以内') + '的加法或减法')
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
        else:
            difficulty = '20以内'

        self.start = True
        self.num = self.question_num
        self.counter = -1
        self.output('%s,本次训练是%s道%s的%s题' % (KID_NAME, purple(self.question_num), purple(difficulty), purple(operator)))
        self.output(KID_NAME + ',请稍候,正在准备数据...')
        self.q_and_a = prepare_question(self.question_num, self.operator, self.difficulty)
        self.countdown(5)
        self.all_start_time = datetime.datetime.now()
        self.round_start_time = self.all_start_time
        self.next_question(self)

    def do_e(self, arg):
        if self.counter is None:
            self.output(red('目前还没有题目,请使用N/O/D命令设计题目或输入S后回车直接使用默认设置'))
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

        if int(arg) == self.q_and_a[self.counter][4]:
            self.each_end_time = datetime.datetime.now()
            self.do_shell('clear')
            if self.num > 0:
                self.output(green(KID_NAME + ',你真棒!还剩') + purple(str(self.num - self.counter - 1)) + green('道哦~~'))
            else:
                self.output(green(KID_NAME + ',你真棒!还剩') + purple(str(self.question_num - self.counter - 1)) + green('道哦~~'))
            self.q_and_a[self.counter][5] += 1
            each_duration = self.each_end_time - self.each_start_time
            self.q_and_a[self.counter][6] = each_duration.seconds
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
            self.q_and_a[self.counter][5] += 1
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
D(ifficulty)        -- D [e(asy)|h(ard)] (例如: D e) (解释: 本次训练难度设为10以内)
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

import tkinter as tk
import tkinter.ttk as ttk
import datetime as da
import calendar as ca
from turtle import width
import pymysql.cursors
from tkinter import scrolledtext

WEEK = ['日', '月', '火', '水', '木', '金', '土']
WEEK_COLOUR = ['red', 'black', 'black', 'black','black', 'black', 'blue']
actions = ('学校','試験', '課題', '行事', '就活', 'アルバイト','旅行')

class YicDiary:

  def __init__(self, root):
    root.title('予定管理アプリ')
    root.geometry('520x280')  # 画面のサイズ
    root.resizable(0, 0)
    root.grid_columnconfigure((0, 1), weight=1)
    self.sub_win = None

    self.year  = da.date.today().year
    self.mon = da.date.today().month
    self.today = da.date.today().day

    self.title = None
    # 左側のカレンダー部分
    leftFrame = tk.Frame(root)
    leftFrame.grid(row=0, column=0)
    self.leftBuild(leftFrame)

    # 右側の予定管理部分
    rightFrame = tk.Frame(root)
    rightFrame.grid(row=0, column=1)
    self.rightBuild(rightFrame)


  #-----------------------------------------------------------------
  # アプリの左側の領域を作成する
  #
  # leftFrame: 左側のフレーム
  def leftBuild(self, leftFrame):
    self.viewLabel = tk.Label(leftFrame, font=('', 10))
    beforButton = tk.Button(leftFrame, text='＜', font=('', 10), command=lambda:self.disp(-1))
    nextButton = tk.Button(leftFrame, text='＞', font=('', 10), command=lambda:self.disp(1))

    self.viewLabel.grid(row=0, column=1, pady=10, padx=10)
    beforButton.grid(row=0, column=0, pady=10, padx=10)
    nextButton.grid(row=0, column=2, pady=10, padx=10)

    self.calendar = tk.Frame(leftFrame)
    self.calendar.grid(row=1, column=0, columnspan=3)
    self.disp(0)


  #-----------------------------------------------------------------
  # アプリの右側の領域を作成する
  #
  # rightFrame: 右側のフレーム
  def rightBuild(self, rightFrame):
    r1_frame = tk.Frame(rightFrame)
    r1_frame.grid(row=0, column=0, pady=10)

    temp = '{}年{}月{}日の予定'.format(self.year, self.mon, self.today)
    self.title = tk.Label(r1_frame, text=temp, font=('', 12))
    self.title.grid(row=0, column=0, padx=20)

    button = tk.Button(rightFrame, text='追加', command=lambda:self.add())
    button.grid(row=0, column=1)

    self.r2_frame = tk.Frame(rightFrame)
    self.r2_frame.grid(row=1, column=0)

    self.scrolledtext = scrolledtext.ScrolledText(rightFrame, width = 30, height = 10)
    self.scrolledtext.grid(column = 0, row = 10, columnspan = 3, sticky = tk.W + tk.E, pady = 50, padx = 30)
    self.schedule()


  #-----------------------------------------------------------------
  # アプリの右側の領域に予定を表示する
  #
  def schedule(self):
    # ウィジットを廃棄
    for widget in self.r2_frame.winfo_children():
      widget.destroy()
    
    self.scrolledtext.delete([1.0], tk.END)

    click_days2 = '{}-{}-{}'.format(self.year, self.mon, self.today)
    # データベースに新規予定を挿入する
    # データベースに接続する
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='',
                                 db='apr01',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        # トランザクション開始
        connection.begin()

        with connection.cursor() as cursor:
            # SQLの作成・定義
            sql = """
                  SELECT kinds, memo
                  FROM schedule_table
                    INNER JOIN  calendar_table
                    ON schedule_table.scheduleID = calendar_table.scheduleID
                    INNER JOIN kinds_table
                    ON schedule_table.kindsID = kinds_table.kindsID
                    WHERE days = %s
                  ORDER BY schedule_table.scheduleID ASC
                  """

            # SQLの実行
            cursor.execute(sql, (click_days2))

            # 実行結果の受け取り（複数行の場合）
            results = cursor.fetchall()
            for i, row in enumerate(results):
              string1 = row['kinds']
              string2 = row['memo']
              string3 = '[' + string1 +']' + ' ' + string2

              self.scrolledtext.insert([1.0], string3)  # これがスクロールテキストに表示される

    except Exception as e:
        print('error:', e)
        connection.rollback()
    finally:
        connection.close()
    

  #-----------------------------------------------------------------
  # カレンダーを表示する
  #
  # argv: -1 = 前月
  #        0 = 今月（起動時のみ）
  #        1 = 次月
  def disp(self, argv):
    self.mon = self.mon + argv
    if self.mon < 1:
      self.mon, self.year = 12, self.year - 1
    elif self.mon > 12:
      self.mon, self.year = 1, self.year + 1

    self.viewLabel['text'] = '{}年{}月'.format(self.year, self.mon)

    cal = ca.Calendar(firstweekday=6)
    cal = cal.monthdayscalendar(self.year, self.mon)

    # ウィジットを廃棄
    for widget in self.calendar.winfo_children():
      widget.destroy()

    # 見出し行
    r = 0
    for i, x in enumerate(WEEK):
      label_day = tk.Label(self.calendar, text=x, font=('', 10), width=3, fg=WEEK_COLOUR[i])
      label_day.grid(row=r, column=i, pady=1)

    # カレンダー本体
    r = 1
    for week in cal:
      for i, day in enumerate(week):
        if day == 0: day = ' ' 
        label_day = tk.Label(self.calendar, text=day, font=('', 10), fg=WEEK_COLOUR[i], borderwidth=1)
        if (da.date.today().year, da.date.today().month, da.date.today().day) == (self.year, self.mon, day):
          label_day['relief'] = 'solid'
        label_day.bind('<Button-1>', self.click)
        label_day.grid(row=r, column=i, padx=2, pady=1)
      r = r + 1

    # 画面右側の表示を変更
    if self.title is not None:
      self.today = 1
      self.title['text'] = '{}年{}月{}日の予定'.format(self.year, self.mon, self.today)


  #-----------------------------------------------------------------
  # 予定を追加したときに呼び出されるメソッド
  #
  def add(self):
    if self.sub_win == None or not self.sub_win.winfo_exists():
      self.sub_win = tk.Toplevel()
      self.sub_win.geometry("300x300")
      self.sub_win.resizable(0, 0)

      # ラベル
      sb1_frame = tk.Frame(self.sub_win)
      sb1_frame.grid(row=0, column=0)
      temp = '{}年{}月{}日　追加する予定'.format(self.year, self.mon, self.today)
      title = tk.Label(sb1_frame, text=temp, font=('', 12))
      title.grid(row=0, column=0)

      # 予定種別（コンボボックス）
      sb2_frame = tk.Frame(self.sub_win)
      sb2_frame.grid(row=1, column=0)
      label_1 = tk.Label(sb2_frame, text='種別 : 　', font=('', 10))
      label_1.grid(row=0, column=0, sticky=tk.W)
      self.combo = ttk.Combobox(sb2_frame, state='readonly', values=actions)
      self.combo.current(0)
      self.combo.grid(row=0, column=1)

      # テキストエリア（垂直スクロール付）
      sb3_frame = tk.Frame(self.sub_win)
      sb3_frame.grid(row=2, column=0)
      self.text = tk.Text(sb3_frame, width=40, height=15)
      self.text.grid(row=0, column=0)
      scroll_v = tk.Scrollbar(sb3_frame, orient=tk.VERTICAL, command=self.text.yview)
      scroll_v.grid(row=0, column=1, sticky=tk.N+tk.S)
      self.text["yscrollcommand"] = scroll_v.set

      # 保存ボタン
      sb4_frame = tk.Frame(self.sub_win)
      sb4_frame.grid(row=3, column=0, sticky=tk.NE)
      button = tk.Button(sb4_frame, text='保存', command=lambda:self.done())
      button.pack(padx=10, pady=10)
    elif self.sub_win != None and self.sub_win.winfo_exists():
      self.sub_win.lift()


  #-----------------------------------------------------------------
  # 予定追加ウィンドウで「保存」を押したときに呼び出されるメソッド
  #
  def done(self):
    # 日付
    click_days = '{}-{}-{}'.format(self.year, self.mon, self.today)
    print(click_days)

    # 種別
    kinds = self.combo.get()
    print(kinds)

    kinds_dict = {'学校':1, '試験':2, '課題':3, '行事':4, '就活':5, 'アルバイト':6, '旅行':7}

    kinds_no = kinds_dict[kinds]

    # 別表にしている場合は、外部キーとして呼び出す値を得る
    # getkey()メソッド（または関数）を使う
    #foreignkey = getkey(kinds)

    # 予定詳細
    memo = self.text.get("1.0", "end")
    print(memo)

    # データベースに新規予定を挿入する
    # データベースに接続する
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='',
                                 db='apr01',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        # トランザクション開始
        connection.begin()

        with connection.cursor() as cursor:
            # SQLの作成・定義
            sql = "INSERT INTO Calendar_table(days) VALUES(%s)"
            # SQLの実行
            cursor.execute(sql, (click_days,))

            # SQLの作成・定義
            sql = "SELECT max(scheduleID) FROM Calendar_table"
            # SQLの実行
            cursor.execute(sql)

            # 実行結果の受け取り（複数行の場合）
            results = cursor.fetchone()

            MAXID = results['max(scheduleID)']

            # SQLの作成・定義
            sql = "INSERT INTO Schedule_table(scheduleID, kindsID, memo) VALUES(%s, %s, %s)"
            # SQLの実行
            cursor.execute(sql, (MAXID, kinds_no, memo))

            connection.commit()

    except Exception as e:
        print('error:', e)
        connection.rollback()
    finally:
        connection.close()


# この行に制御が移った時点でDBとの接続は切れている
    self.sub_win.destroy()


  #-----------------------------------------------------------------
  # 日付をクリックした際に呼びだされるメソッド（コールバック関数）
  #
  # event: 左クリックイベント <Button-1>
  def click(self, event):
    day = event.widget['text']
    if day != ' ':
      self.title['text'] = '{}年{}月{}日の予定'.format(self.year, self.mon, day)
      self.today = day

      self.schedule()

def Main():
  root = tk.Tk()
  YicDiary(root)
  root.mainloop()

if __name__ == '__main__':
  Main()



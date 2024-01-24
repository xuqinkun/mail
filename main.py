# -*- coding: utf-8 -*-
import argparse
import shutil
from typing import List
from pathlib import Path
from smtplib import SMTP_SSL
from file_util import zip_split
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication


def send_mail(message, subject, sender_show, recipient_show: str, to_addrs: str, cc_show: str, batch_size: int, file_list: List[Path]):

    # 填写真实的发邮件服务器用户名、密码
    user = '1394077607@qq.com'
    password = 'vupylooamolwbabd'
    # 邮件内容

    with SMTP_SSL(host="smtp.qq.com", port=465) as smtp:
        # 登录发邮件服务器
        smtp.login(user=user, password=password)
        # 实际发送、接收邮件配置
        points = []
        for i in range(0, len(file_list) + 1, batch_size):
            points.append(i)
        if len(file_list) not in points:
            points.append(len(file_list))
        n = 0
        for left, right in zip(points[0:len(points)-1], points[1:len(points)]):
            n += 1
            msg = MIMEMultipart()
            # 邮件主题描述
            msg["Subject"] = subject + '-' + str(n)

            # 发件人显示，不起实际作用
            msg["From"] = sender_show
            # 收件人显示，不起实际作用
            msg["To"] = recipient_show
            # 抄送人显示，不起实际作用
            msg["Cc"] = cc_show
            for i in range(left, right):
                file = file_list[i]
                part = MIMEApplication(file.read_bytes())
                file_name = file.name
                part.add_header('Content-Disposition', 'attachment', filename=file_name)  # 给附件重命名,一般和原文件名一样,改错了可能无法打开.
                msg.attach(part)
                print(f'Add file[{file_name}]')
            smtp.sendmail(from_addr=user, to_addrs=to_addrs.split(','), msg=msg.as_string())
            print(f'Send {n}th file succeed')

        print("发送成功！")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--src', type=str)
    parser.add_argument('-o', '--out', type=str)
    parser.add_argument('-n', '--num_mb', type=int)
    parser.add_argument('-t', '--to', type=str)
    parser.add_argument('-b', '--batch_size', type=int)
    parser.add_argument('-ow', "--over_write", action="store_true", help="Overwrite split files")
    parser.add_argument('-i', "--interactive", default=False, action="store_true",help="交互式运行")

    args = parser.parse_args()
    src = Path(args.src)
    num_mb = args.num_mb
    batch_size = args.batch_size
    out_dir = Path(args.out)
    Subject = src.name
    # 显示发送人
    sender_show = 'xuqinkun<1394077607@qq.com>'
    # 显示收件人
    recipient_show = 'xuqinkun'
    # 实际发给的收件人
    to_addrs = args.to
    if args.interactive:
        while True:
            src = input("src>")
            if src == 'q':
                exit(0)
            path = Path(src)
            Subject = path.name
            if args.over_write:
                print('Overwrite split files')
                print(f'Remove dir {out_dir}')
                shutil.rmtree(out_dir, ignore_errors=True)
                out_dir.mkdir()
            if not path.exists():
                print(f'{path.absolute()} not found')
                continue
            files = zip_split(path, out_dir, num_mb)
            send_mail("V50", Subject, sender_show, recipient_show, to_addrs, cc_show='', file_list=files,
                      batch_size=batch_size)

    if not src.exists():
        print(f'{src.absolute()} not found')
        exit(1)

    print(f'Args:\n\tsrc: {src}\n\tout: {out_dir}\n\tnum_mb: {num_mb}\n\tbatch_size {batch_size}')
    if args.over_write:
        print('Overwrite split files')
        print(f'Remove dir {out_dir}')
        shutil.rmtree(out_dir, ignore_errors=True)
        out_dir.mkdir()
        files = zip_split(src, out_dir, num_mb)
    else:
        files = [l for l in out_dir.glob(f"{src.stem}s.*")]
    def sort(e: Path):
        suf = e.name.split('.')[-1]
        if suf == 'zip':
            return 0
        nth = int(suf.split('z')[-1])
        return nth
    files = sorted(files, key=sort)
    points = []

    if len(files) == 0:
        print('No file to send')
        exit(0)
    send_mail("V50", Subject, sender_show, recipient_show, to_addrs, cc_show='', file_list=files, batch_size=batch_size)

#!/usr/bin/env python3
"""Exercise the same tool handlers without publishing private mail contents."""
import argparse
import json
import sys
from server import run, error_message


def main():
    parser=argparse.ArgumentParser(description='检查真实登录和文件夹；--sample 额外验证收件箱及已发送正文读取。')
    parser.add_argument('--sample', action='store_true')
    args=parser.parse_args()
    try:
        print(json.dumps(run('neu_mail_status',{}),ensure_ascii=False),flush=True)
        folders=run('neu_mail_list_folders',{})['folders']
        print(json.dumps({'folders':folders},ensure_ascii=False),flush=True)
        if args.sample:
            targets=[f for f in folders if f['id'].upper()=='INBOX' or '\\Sent' in f['flags']]
            for folder in targets:
                page=run('neu_mail_list_messages',{'folder':folder['id'],'limit':5})
                report={'folder':folder['name'],'returned_messages':len(page['messages']),'has_more':page['has_more']}
                if page['messages']:
                    body=run('neu_mail_read',{'folder':folder['id'],'uid':page['messages'][0]['uid'],'uidvalidity':page['uidvalidity']})
                    report.update(body_read=True,body_parts=len(body['body']))
                print(json.dumps(report,ensure_ascii=False),flush=True)
    except Exception as exc:
        print(error_message(exc),file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())

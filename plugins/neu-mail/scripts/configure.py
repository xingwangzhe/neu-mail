#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Interactively configure an account without exposing credentials in argv."""
import argparse
import getpass
import json
import os
import tempfile
from pathlib import Path


def save_account(path, account):
    path = Path(path).expanduser()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if path.is_symlink():
        raise ValueError('拒绝写入符号链接配置文件。')
    fd, temporary = tempfile.mkstemp(prefix='.neu-mail-', dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(account, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return path


def main():
    parser = argparse.ArgumentParser(description='配置东北大学学生邮箱，只需输入完整邮箱和客户端专用密码。')
    parser.add_argument('--host', default='mails.neu.edu.cn', help='IMAP 主机，默认 mails.neu.edu.cn')
    parser.add_argument('--port', type=int, default=993, help='IMAP TLS 端口，默认 993')
    parser.add_argument('--allow-hostname-mismatch', action='store_true', help='显式允许证书域名不匹配，仍校验签发链及有效期')
    parser.add_argument('--force', action='store_true', help='覆盖已有账号配置')
    args = parser.parse_args()
    if os.name != 'posix':
        parser.error('当前凭据文件权限实现支持 Linux/macOS；Windows 用户请使用 WSL。')
    if not args.host or not 1 <= args.port <= 65535:
        parser.error('主机不能为空，端口必须在 1–65535 范围。')
    path = Path(os.environ.get('NEU_MAIL_CONFIG', '~/.config/neu-mail/account.json')).expanduser()
    if path.exists() and not args.force:
        parser.error('已有账号配置；确需替换时请加 --force。')
    print(f'服务器：{args.host}:{args.port}')
    print('TLS：加密、校验签发链和有效期；' + ('跳过域名匹配（已通过参数选择兼容模式）。' if args.allow_hostname_mismatch else '严格校验域名。'))
    username = input('完整邮箱地址：').strip()
    password = getpass.getpass('客户端专用密码（输入不回显）：').strip()
    if '@' not in username or not password or any(c in username for c in '\r\n\x00'):
        parser.error('请输入完整邮箱地址和非空客户端专用密码。')
    save_account(path, {'host':args.host, 'port':args.port, 'username':username, 'password':password,
                        'allow_hostname_mismatch':args.allow_hostname_mismatch})
    print('配置已保存，文件权限 0600。密码是本机明文存储，不会写入插件目录。')
    print('下一步：uv run --no-project scripts/check.py --sample')


if __name__ == '__main__':
    main()

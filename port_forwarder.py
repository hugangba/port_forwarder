import asyncio
import socket
import ipaddress
import os

async def handle_client(reader, writer):
    # 获取客户端和服务器的地址信息
    peername = writer.get_extra_info('peername')
    sockname = writer.get_extra_info('sockname')
    client_addr = peername[0]  # 客户端源 IP
    server_addr = sockname[0]  # 服务器目标 IP
    server_port = sockname[1]  # 服务器目标端口

    # 将地址转换为 ipaddress 对象
    try:
        client_ip = ipaddress.ip_address(client_addr)
        server_ip = ipaddress.ip_address(server_addr)
    except ValueError:
        writer.close()
        await writer.wait_closed()
        return

    # 基于服务器目标 IPv6 地址的最后四个段生成 IPv4 A.B.C.D
    try:
        segments = server_ip.exploded.split(':')[-4:]  # 取最后四个段
        if len(segments) != 4:
            writer.close()
            await writer.wait_closed()
            return
        # 去掉每段的前导零，直接解析为十进制
        values = []
        for seg in segments:
            cleaned_seg = seg.lstrip('0') or '0'  # 去掉前导零，空字符串转为 '0'
            val = int(cleaned_seg, 10)  # 直接解析为十进制（基数 10）
            if not 0 <= val <= 255:
                writer.close()
                await writer.wait_closed()
                return
            values.append(val)
        a, b, c, d = values
        target_host = f"{a}.{b}.{c}.{d}"
        target_port = server_port  # 使用服务器目标端口
    except ValueError:
        writer.close()
        await writer.wait_closed()
        return

    # 检查目标 IPv4 是否为公网地址
    target_ip = ipaddress.ip_address(target_host)
    if target_ip.is_private or target_ip.is_reserved or target_ip.is_multicast or target_ip.is_loopback:
        writer.close()
        await writer.wait_closed()
        return

    # 仅记录成功转发的连接
    print(f"从客户端 [{client_ip}]:{server_port} (服务器 [{server_ip}]:{server_port}) 转发到 {target_host}:{target_port}")
    try:
        # 连接到目标 IPv4 地址和端口
        target_reader, target_writer = await asyncio.open_connection(target_host, target_port)

        # 双向数据转发
        async def forward(reader, writer):
            try:
                while True:
                    data = await reader.read(1024)
                    if not data:
                        break
                    writer.write(data)
                    await writer.drain()
            except Exception as e:
                print(f"转发错误，从 [{client_ip}]:{server_port} 到 {target_host}:{target_port}: {e}")
            finally:
                writer.close()
                await writer.wait_closed()

        # 启动双向转发
        await asyncio.gather(
            forward(reader, target_writer),
            forward(target_reader, writer)
        )
    except Exception as e:
        print(f"转发到 {target_host}:{target_port} 错误: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

async def start_server(port):
    listen_addr = "::"  # 监听所有 IPv6 地址
    try:
        server = await asyncio.start_server(
            handle_client,
            listen_addr, port, family=socket.AF_INET6
        )
        addr = server.sockets[0].getsockname()
        print(f"监听 [{addr[0]}]:{addr[1]}")
        async with server:
            await server.serve_forever()
    except Exception as e:
        print(f"启动服务器失败，地址 [{listen_addr}]:{port}: {e}")

async def main():
    # 检查 IPv6 是否启用
    if os.path.exists("/proc/sys/net/ipv6/conf/all/disable_ipv6"):
        with open("/proc/sys/net/ipv6/conf/all/disable_ipv6", "r") as f:
            if f.read().strip() == "1":
                print("错误: 系统已禁用 IPv6，请启用 IPv6。")
                return

    # 监听常见端口
    ports = [80, 443, 8080, 8443]
    tasks = [start_server(port) for port in ports]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("正在关闭...")
    except Exception as e:
        print(f"主程序错误: {e}")

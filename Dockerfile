# ============================================================
# Dockerfile
# 被测服务镜像 —— 根据实际项目修改此文件
# 当前示例为 Go 项目，如需其他语言请替换 builder 和 runtime 阶段
# ============================================================

# ---- 构建阶段：编译 Go 程序 ----
FROM golang:1.24-alpine AS builder
WORKDIR /app

# 先复制依赖文件（利用 Docker 层缓存，依赖不变时不重新下载）
COPY go.mod go.sum ./
RUN go mod download

# 再复制源码并编译
COPY . .
RUN go build -o app .

# ---- 运行阶段：最小化镜像 ----
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/app .

EXPOSE 8080
CMD ["./app"]

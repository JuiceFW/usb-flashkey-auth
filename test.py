from flash_auth import FlashKeyAuth


def main():
    auth = FlashKeyAuth()

    mode = input("""\
Выберите режим:
[1] - Создать ключ (ОДИН РАЗ)
[2] - Проверить ключ (из всех флешек)

Ввод: """)


    if mode == "1":
        # ОДИН РАЗ
        auth.init_key()
    elif mode == "2":
        status = auth.check_key()
        if not status:
            print("❌ Ключ не найден или неверный")
        else:
            print("✅ Доступ разрешён")


if __name__ == "__main__":
    main()

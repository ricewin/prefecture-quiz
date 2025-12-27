from common.routing import footer, navigation, page_config


def main():
    initialize()
    process_data()
    # finalize()


def initialize():
    # print("Initializing...")
    page_config()


def process_data():
    # print("Processing data...")
    navigation()


def finalize():
    # print("Finalizing...")
    footer()


if __name__ == "__main__":
    main()

"""
    Main script that contains the classes to run the Website automation
"""

from pathlib import Path
from robocorp.tasks import task
import yaml
from classes import GothAmistController,logger


@task
def runner():
    """
    Assign a task into RoboCorp
    """
    with open(f"{Path.cwd()}/config.yaml", "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    run = GothAmistController(
        config["Parameters"]["SearchPhrase"], config["Parameters"]["NewsAmount"]
    )
    run.launch()
    run.result_amount()

    if int(run.results) == 0:
        logger.info("No results for the search phrase")

    else:
        for index in range(1, run.data_amount + 1):
            run.close_popup()
            run.load_more(index)
            run.get_title(index)
            run.get_description(index)
            run.get_picture(index*2)
            run.counting_phrases()
            run.validate_news_context()
            input("e ai?")
            run.download_image()
            run.append_data()
            if index == run.results:
                break

        run.create_dataframe()
    logger.info("Process Finished!!!")

runner()
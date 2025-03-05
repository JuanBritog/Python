import json
import logging
from JobFactory import JobFactory

class Scheduler:
    def __init__(self, name):
        self.name = name
        self.jobs = []
        self.logger = logging.getLogger(f"Scheduler_{self.name}")
        self.setup_logging()

    def setup_logging(self):
        handler = logging.FileHandler(f"{self.name}.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def add_job(self, job_params):
        self.logger.info("Attempting to add job with params: %s", job_params)
        try:
            job = JobFactory.create_job(job_params)
            self.jobs.append(job)
            self.logger.info(f"Added job: {job.NomeJob}")
        except Exception as e:
            self.logger.error(f"Failed to add job: {e}")
            print(f"Failed to add job: {e}")

    def run_jobs(self):
        self.logger.info("Attempting to run jobs")
        for job in self.jobs:
            try:
                self.logger.info(f"Running job: {job.NomeJob}")
                job.run()
                self.logger.info(f"Completed job: {job.NomeJob}")
            except Exception as e:
                self.logger.error(f"Error running job {job.NomeJob}: {e}")
                print(f"Error running job {job.NomeJob}: {e}")


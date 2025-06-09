from  time import sleep, time, strftime, localtime
import json
import logging
logger = logging.getLogger(__name__)

class TaskTimeoutError(Exception):
    pass

class TaskError(Exception):
    pass

def wait_for_task(dnac, taskid, retry=2, timeout=10):
    start_time = time()
    first = True
    while True:
        result = dnac.task.get_task_by_id(taskid)
        # print json.dumps(response)
        if result.response.endTime is not None:
            return result
        else:
            # print a message the first time throu
            if first:
                logger.debug("Task:{} not complete, waiting {} seconds, polling {}".format(taskid, timeout, retry))
                first = False
            if timeout and (start_time + timeout < time()):
                raise TaskTimeoutError("Task %s did not complete within the specified timeout "
                                       "(%s seconds)" % (taskid, timeout))
            logging.debug("Task=%s has not completed yet. Sleeping %s seconds..." % (taskid, retry))
            sleep(retry)
        if result.response.isError == "True":
            raise TaskError("Task %s had error %s" % (taskid, result.response.progress))
    return response

def wait_for_activity(dnac, activityid, retry=2, timeout=40):
    start_time = time()
    first = True
    while True:
        url = f'/dna/intent/api/v1/activities/{activityid}'
        result = dnac.custom_caller.call_api(raise_exception=False, method="GET", resource_path=url)
        #print(json.dumps(result))
        if result.response.status in ["COMPLETED","READY","DISCARD_RESOURCES_SUCCESS"]:
            return result
        else:
            # print a message the first time throu
            if first:
                logger.debug("Task:{} not complete, waiting {} seconds, polling {}".format(activityid, timeout, retry))
                first = False
            if timeout and (start_time + timeout < time()):
                raise TaskTimeoutError("Task %s did not complete within the specified timeout "
                                       "(%s seconds)" % (activityid, timeout))
            logging.debug("Task=%s has not completed yet. Sleeping %s seconds..." % (activityid, retry))
            sleep(retry)
        if result.response.status == "FAILED":
            raise TaskError("Task %s had error %s" % (activityid, result.response))
        logger.debug(result)
    return result

import time

from loguru import logger


def execute_with_retries(completion_executor, request_data, max_retries=100, wait_time=5):
    """
    모델 요청을 수행하며, 응답이 없을 경우 최대 max_retries까지 재시도하는 함수.
    """
    response_data = None
    retry_count = 0

    while retry_count < max_retries:
        response_data = completion_executor.execute(request_data)

        if response_data:
            logger.info("✅ 모델 응답 수신 완료")
            return response_data

        retry_count += 1
        logger.warning(f"⚠️ 모델 응답 없음. {retry_count}번째 재시도 중...")
        time.sleep(wait_time)

    logger.error("❌ 최대 재시도 횟수를 초과하여 응답을 받지 못했습니다.")
    return None

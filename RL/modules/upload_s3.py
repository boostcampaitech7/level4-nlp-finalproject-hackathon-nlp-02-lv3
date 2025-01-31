import datetime
import hashlib
import hmac
import logging

import requests


def upload_file_to_s3(file_path, bucket_name, object_name, access_key, secret_key):
    """네이버 클라우드 Object Storage에 파일 업로드 (AWS Signature v4 적용)"""

    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    logger.info(f"📤 파일 업로드 시작: {file_path} -> {bucket_name}/{object_name}")

    # 네이버 클라우드 Object Storage 정보
    endpoint = "https://kr.object.ncloudstorage.com"

    # 날짜 및 서명 생성
    now = datetime.datetime.utcnow()
    timestamp = now.strftime("%Y%m%dT%H%M%SZ")
    datestamp = now.strftime("%Y%m%d")

    # 요청 헤더 생성
    headers = {
        "x-amz-date": timestamp,
        "x-amz-content-sha256": "UNSIGNED-PAYLOAD",
        "Host": f"{bucket_name}.{endpoint.replace('https://', '')}",
        "Content-Type": "text/plain",
    }

    # 요청 URL (Virtual Host 스타일)
    url = f"{endpoint}/{bucket_name}/{object_name}"

    # 파일 읽기
    try:
        with open(file_path, "rb") as file:
            file_data = file.read()
        logger.info(f"📂 파일 읽기 성공: {file_path}")
    except IOError as e:
        logger.error(f"❌ 파일 읽기 실패: {e}")
        return False, f"❌ 파일 읽기 실패: {e}"

    # AWS Signature Version 4를 사용한 서명 생성
    def sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    def get_signature_key(key, date_stamp, region, service):
        k_date = sign(("AWS4" + key).encode("utf-8"), date_stamp)
        k_region = sign(k_date, region)
        k_service = sign(k_region, service)
        k_signing = sign(k_service, "aws4_request")
        return k_signing

    region = "kr-standard"
    service = "s3"

    credential_scope = f"{datestamp}/{region}/{service}/aws4_request"

    canonical_request = (
        f"PUT\n/{bucket_name}/{object_name}\n\n"
        f"host:{bucket_name}.{endpoint.replace('https://', '')}\n"
        f"x-amz-content-sha256:UNSIGNED-PAYLOAD\n"
        f"x-amz-date:{timestamp}\n\n"
        f"host;x-amz-content-sha256;x-amz-date\nUNSIGNED-PAYLOAD"
    )

    hashed_canonical_request = hashlib.sha256(
        canonical_request.encode("utf-8")
    ).hexdigest()

    string_to_sign = (
        f"AWS4-HMAC-SHA256\n{timestamp}\n{credential_scope}\n{hashed_canonical_request}"
    )

    signing_key = get_signature_key(secret_key, datestamp, region, service)
    signature = hmac.new(
        signing_key, string_to_sign.encode("utf-8"), hashlib.sha256
    ).hexdigest()

    authorization_header = (
        f"AWS4-HMAC-SHA256 Credential={access_key}/{credential_scope}, "
        f"SignedHeaders=host;x-amz-content-sha256;x-amz-date, "
        f"Signature={signature}"
    )

    headers["Authorization"] = authorization_header

    logger.info("🔑 인증 헤더 생성 완료")

    # 파일 업로드 요청
    try:
        response = requests.put(url, data=file_data, headers=headers)
        logger.info(f"📡 업로드 요청 완료: 상태 코드 {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ 업로드 요청 실패: {e}")
        return False, f"❌ 업로드 요청 실패: {e}"

    # 결과 반환
    if response.status_code == 200:
        logger.info("✅ 파일 업로드 성공!")
        return True, "✅ 파일 업로드 성공!"
    else:
        logger.error(f"❌ 업로드 실패: {response.status_code} - {response.text}")
        return False, f"❌ 업로드 실패: {response.status_code} - {response.text}"

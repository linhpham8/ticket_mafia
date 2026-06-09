*** Settings ***
Documentation     Biến trong này dược dùng chung cho cả web và app,
Variables    ../../Variables/ENV_${ENV}.yaml    # Đỏ thì kệ đỏ :))


*** Variables ***
${RUNNING_ON_JENKIN}    N
${CLOSE_BROWSER}    Y
${OTP}            123456
${UPDATE_TEST_CASE}    N
${UNINSTALL_APP}    N
${RESPONSE}       ${EMPTY}
${TESTCYCLES}     ${EMPTY}
${timeout}        30s
${dbName}         b2bauto
${dbUsername}     admin    # admin
${dbPassword}     P@ssw0rd@    # P@ssw0rd@
${dbHost}         10.124.57.229
${dbPort}         3306
${dbCharset}      utf8
${channel}        AAQAKROfGhA
${mention}        mention
${team}           ${empty}
${PIPELINE_CODE}    ${EMPTY}
${RUN_BROWSER}    chrome
${ENV}    QC
${auth}    vtcbvnvx:dwj9M29EWjZCROf9%
${ApiKeyMember}    ed71f76fb2e84c85961fb2e881b842ce
${API_REPORT}    https://api-pss-report.int.nexa.mobi
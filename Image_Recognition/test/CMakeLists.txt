add_test(NAME ${PROJECT_NAME}_test COMMAND ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/${PROJECT_NAME}Test.py -o "manager.components.precreate:${PROJECT_NAME}" -o "manager.components.preconnect:${PROJECT_NAME}0.Target_In1?port=${PROJECT_NAME}Test0.Target_In1,${PROJECT_NAME}0.target_point?port=${PROJECT_NAME}Test0.target_point" -o "manager.components.preactivation:${PROJECT_NAME}0,${PROJECT_NAME}Test0" WORKING_DIRECTORY ${CMAKE_BINARY_DIR})
add_test(NAME ${PROJECT_NAME}_geometry_test
         COMMAND ${Python_EXECUTABLE} -B ${CMAKE_CURRENT_SOURCE_DIR}/test_geometry_recognition.py
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
add_test(NAME ${PROJECT_NAME}_component_logic_test
         COMMAND ${Python_EXECUTABLE} -B ${CMAKE_CURRENT_SOURCE_DIR}/test_component_logic.py
         WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
string(REPLACE ";" "\\;" PYTHONPATH "$ENV{PYTHONPATH}")
if(UNIX)
  set_tests_properties(${PROJECT_NAME}_test PROPERTIES ENVIRONMENT "PYTHONPATH=${CMAKE_SOURCE_DIR}:${PYTHONPATH}")
else()
  set_tests_properties(${PROJECT_NAME}_test PROPERTIES ENVIRONMENT "PYTHONPATH=${CMAKE_SOURCE_DIR}\;${PYTHONPATH}")
endif()

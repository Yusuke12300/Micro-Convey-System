add_subdirectory(Startup_Generation_AfterTest)

MAP_ADD_STR(hdrs "${PROJECT_NAME}Test/" headers)
set(headers ${headers} PARENT_SCOPE)

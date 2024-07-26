from fastapi import HTTPException
from starlette import status

ERROR_403_FORBIDDEN = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Access is denied')
ERROR_401_UNAUTHORIZED = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid Token')
ERROR_406_NOT_ACCEPTABLE = HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f'Not Acceptable')
ERROR_409_CONFLICT = HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Conflict')
ERROR_404_USER_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User with id {id} not found')
ERROR_404_PAIR_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Pair with {id} not found')
ERROR_422_UNPROCESSABLE_ENTITY = HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                               detail='Unprocessable Entity')

ERROR_404_COMPOSITE_NOT_FOUND = HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                              detail='Composite with {id} not found')

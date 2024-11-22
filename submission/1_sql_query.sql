/*
Thoughts for this question:
if use single query for all the time, for example, the query:

SELECT User_ID
FROM Users
WHERE User_Email REGEXP BINARY '[A-Z]';

it will cost a lot of time when data are tremendous 

the follwoing steps will be:
1. create a new field to mark whether email has upper case character
2. UPDATE the new field for each row 
3. create a new index and delimeter on the new field 
4. use the new query 

*/

-- add new filed Has_Uppercase, set it default as False
ALTER TABLE Users ADD Has_Uppercase BOOLEAN DEFAULT FALSE;

-- UPDATE the filed for all the values 
UPDATE Users
SET Has_Uppercase = BINARY User_Email REGEXP '[A-Z]';

-- create new index 
CREATE INDEX idx_has_uppercase ON Users(Has_Uppercase);

-- trigger for insert 
-- when new data are inserted, it will be triggered 
CREATE TRIGGER trg_insert_has_uppercase
BEFORE INSERT ON Users
FOR EACH ROW
SET NEW.Has_Uppercase = BINARY NEW.User_Email REGEXP '[A-Z]';


-- update trigger
-- when user data are updated 
CREATE TRIGGER trg_update_has_uppercase
BEFORE UPDATE ON Users
FOR EACH ROW
SET NEW.Has_Uppercase = BINARY NEW.User_Email REGEXP '[A-Z]';

-- select the data query 
SELECT User_ID
FROM Users
WHERE Has_Uppercase = TRUE;

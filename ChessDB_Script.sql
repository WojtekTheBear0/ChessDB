CREATE DATABASE ChessDB;
USE ChessDB;


CREATE TABLE endgame (
    FEN VARCHAR(255) PRIMARY KEY,       
    Result VARCHAR(3),                   
    Type VARCHAR(255)                    
);


CREATE TABLE book (
    Title VARCHAR(255) PRIMARY KEY,      
    Author VARCHAR(255),                 
    Description TEXT,                    
    Focus_Area VARCHAR(255),            
    Publication_Year INT,              
    Openings VARCHAR(255)               
);


CREATE TABLE opening (
    FEN VARCHAR(255) NOT NULL PRIMARY KEY, 
    Name VARCHAR(255) NOT NULL,            
    ECO VARCHAR(10)                        
);


CREATE TABLE master (            
    `Name` VARCHAR(255) PRIMARY KEY,          
    Country VARCHAR(255),                 
    Rating INT                            
);


CREATE TABLE `match` (
    `Event` VARCHAR(255) NOT NULL,          
    Round VARCHAR(50) NOT NULL,           
    White_Name VARCHAR(255) NOT NULL,               
    Black_Name VARCHAR(255) NOT NULL,          
    Result CHAR(3),                   
    PGN TEXT,                           
    Opening VARCHAR(255),                         
    PRIMARY KEY (`Event`, Round),           
    FOREIGN KEY (White_Name) REFERENCES master(`Name`),
    FOREIGN KEY (Black_Name) REFERENCES master(`Name`)
);


CREATE TABLE yearlytop100 (
    Year INT NOT NULL,                   
    `Rank` INT NOT NULL,                    
    Player_Name VARCHAR(255) NOT NULL,              
    Rating INT,                        
    PRIMARY KEY (Year, `Rank`),          
    FOREIGN KEY (Player_Name) REFERENCES master(`Name`)
);

-- Junction Table: Book to Opening
CREATE TABLE book_opening (
    Book_Title VARCHAR(255) NOT NULL,   
    Opening_FEN VARCHAR(255) NOT NULL,  
    FOREIGN KEY (Book_Title) REFERENCES book(Title),
    FOREIGN KEY (Opening_FEN) REFERENCES opening(FEN)
);

-- Junction Table: Book to Master
CREATE TABLE book_master (
    Book_Title VARCHAR(255) NOT NULL,    
    Master_Name VARCHAR(255) NOT NULL,   
    FOREIGN KEY (Book_Title) REFERENCES book(Title),
    FOREIGN KEY (Master_Name) REFERENCES master(`Name`)
);

-- Junction Table: Match to Endgame
CREATE TABLE match_endgame (
    Match_Event VARCHAR(255) NOT NULL,   
    Match_Round VARCHAR(50) NOT NULL,     
    Endgame_FEN VARCHAR(255) NOT NULL,   
    FOREIGN KEY (Match_Event, Match_Round) REFERENCES `match`(`Event`, Round),
    FOREIGN KEY (Endgame_FEN) REFERENCES endgame(FEN)
);

-- Insert relationships for Match to Opening
ALTER TABLE `match` ADD CONSTRAINT fk_match_opening FOREIGN KEY (Opening) REFERENCES opening(FEN);
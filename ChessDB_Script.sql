-- Create the database
CREATE DATABASE ChessDB;
USE ChessDB;

-- Table: Endgame
CREATE TABLE endgame (
    FEN VARCHAR(255) PRIMARY KEY,        -- FEN notation as the unique identifier
    Result VARCHAR(3),                   -- Best play result of position (e.g., "1-0", "0-1", "1/2")
    Type VARCHAR(255)                    -- Known type of the endgame (e.g., "Philidor's")
);

-- Table: Book
CREATE TABLE book (
    Title VARCHAR(255) PRIMARY KEY,      -- Title of the book
    Author VARCHAR(255),                 -- Author of the book
    Description TEXT,                    -- Description of the book
    Focus_Area VARCHAR(255),             -- Focus area (tactics, openings, etc.)
    Publication_Year INT,                -- Year published
    Openings VARCHAR(255),               -- Openings mentioned in the book
    Endgames VARCHAR(255)                -- Endgames mentioned in the book
);

-- Table: Opening
CREATE TABLE opening (
    FEN VARCHAR(255) NOT NULL PRIMARY KEY, -- Full FEN notation
    Name VARCHAR(255) NOT NULL,            -- Name of the opening
    ECO VARCHAR(10)                        -- ECO code
);

-- Table: Master
CREATE TABLE master (            
    `Name` VARCHAR(255) PRIMARY KEY,           -- Name of the player
    Country VARCHAR(255),                 -- Country the player represents
    Peak_Rating INT                       -- Highest rating achieved
);

-- Table: Match
CREATE TABLE `match` (
    Event VARCHAR(255) NOT NULL,          -- Event name
    Round VARCHAR(50) NOT NULL,           -- Round number of the event
    White_Name VARCHAR NOT NULL,                -- ID of the player with white pieces
    Black_Name VARCHAR NOT NULL,                -- ID of the player with black pieces
    Result CHAR(3),                       -- Result of the match ("1-0", "0-1", "1/2")
    PGN TEXT,                             -- Moves of the game in PGN format
    Opening VARCHAR(255),                 -- Opening played in the match
    Start_Endgame INT,                    -- First move of endgame positions
    PRIMARY KEY (Event, Round),           -- Composite primary key
    FOREIGN KEY (White_Name) REFERENCES master(`Name`),
    FOREIGN KEY (Black_Name) REFERENCES master(`Name`)
);

-- Table: YearlyTop100
CREATE TABLE yearlytop100 (
    Year INT NOT NULL,                    -- Year of the rankings
    `Rank` INT NOT NULL,                    -- Player's rank
    Player_Name TEXT NOT NULL,               -- Player's name
    Rating INT,                           -- Rating at the time
    PRIMARY KEY (Year, `Rank`),             -- Composite primary key
    FOREIGN KEY (Player_Name) REFERENCES master(`Name`)
);

-- Junction Table: Book to Endgame
CREATE TABLE book_endgame (
    Book_Title VARCHAR(255) NOT NULL,     -- Reference to Book table
    Endgame_FEN VARCHAR(255),            -- Reference to Endgame table
    FOREIGN KEY (Book_Title) REFERENCES book(Title),
    FOREIGN KEY (Endgame_FEN) REFERENCES endgame(FEN)
);

-- Junction Table: Book to Opening
CREATE TABLE book_opening (
    Book_Title VARCHAR(255) NOT NULL,     -- Reference to Book table
    Opening_FEN VARCHAR(255) NOT NULL,   -- Reference to Opening table
    FOREIGN KEY (Book_Title) REFERENCES book(Title),
    FOREIGN KEY (Opening_FEN) REFERENCES opening(FEN)
);

-- Junction Table: Book to Master
CREATE TABLE book_master (
    Book_Title VARCHAR(255) NOT NULL,     -- Reference to Book table
    Master_Name VARCHAR(255) NOT NULL,    -- Reference to Master table
    FOREIGN KEY (Book_Title) REFERENCES book(Title),
    FOREIGN KEY (Master_Name) REFERENCES master(`Name`)
);

-- Junction Table: Match to Endgame
CREATE TABLE match_endgame (
    Match_Event VARCHAR(255) NOT NULL,    -- Reference to Match Event
    Match_Round VARCHAR(50) NOT NULL,     -- Reference to Match Round
    Endgame_FEN VARCHAR(255) NOT NULL,   -- Reference to Endgame Type
    FOREIGN KEY (Match_Event, Match_Round) REFERENCES `match`(Event, Round),
    FOREIGN KEY (Endgame_FEN) REFERENCES endgame(FEN)
);

-- Insert relationships for Match to Opening
ALTER TABLE `match` ADD CONSTRAINT fk_match_opening FOREIGN KEY (Opening) REFERENCES opening(FEN);

<?php

if (isset($_POST['PlayServiceUpdate'])) {
    echo func1($_POST['PlayServiceUpdate']);
}

if (isset($_POST['GetLastRow'])) {
    echo getLastRow();
}

function func1($param){
    $request = json_decode($param);
    
    try {
        // Create file "play_stream.db" as database
        $db = new PDO('sqlite:play_stream.db');
        // Throw exceptions on error
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        $sql = <<<SQL
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY,
    PlayString TEXT,
    PlayCommand TEXT,
    title TEXT,
    duration TEXT,
    streamUrl TEXT,
    created_at INTEGER
)
SQL;
        $db->exec($sql);
        
        // Fix: Store time() result in a variable
        $currentTime = time();
        
        $sql = <<<SQL
INSERT INTO posts (PlayString, PlayCommand, title, duration, streamUrl, created_at)
VALUES (:PlayString, :PlayCommand, :title, :duration, :streamUrl, :created_at)
SQL;
        
        $stmt = $db->prepare($sql);
        
        // Bind the actual values from the request
        $stmt->bindParam(':PlayString', $request->PlayString);
        $stmt->bindParam(':PlayCommand', $request->PlayCommand);
        $stmt->bindParam(':title', $request->title);
        $stmt->bindParam(':duration', $request->duration);
        $stmt->bindParam(':streamUrl', $request->streamUrl);
        $stmt->bindParam(':created_at', $currentTime);
        
        // Execute once with the actual data
        $stmt->execute();
        
        $result = $db->query('SELECT * FROM posts');
        
        foreach($result as $row) {
            list($id, $PlayString, $PlayCommand, $title, $duration, $streamUrl, $createdAt) = $row;
            $output  = "Id: $id <br/>\n";
            $output .= "PlayString: $PlayString<br/>\n";
            $output .= "PlayCommand: $PlayCommand<br/>\n";
            $output .= "Title: $title<br/>\n";
            $output .= "Duration: $duration<br/>\n";
            $output .= "Stream URL: $streamUrl<br/>\n";
            $output .= "Created at: ".date('d.m.Y H:i:s', $createdAt)."<br/>\n";
            
            echo $output;
        }
        
        //$db->exec("DROP TABLE posts");
    } catch(PDOException $e) {
        echo $e->getMessage();
        echo $e->getTraceAsString();
    }
}

function getLastRow() {
    try {
        // Connect to the database
        $db = new PDO('sqlite:play_stream.db');
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // Query to get the last inserted row
        $sql = "SELECT title, duration, streamUrl, created_at FROM posts ORDER BY id DESC LIMIT 1";
        $stmt = $db->query($sql);
        
        if ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            // Return JSON response
            $response = array(
                'success' => true,
                'data' => array(
                    'title' => $row['title'],
                    'duration' => $row['duration'],
                    'streamUrl' => $row['streamUrl'],
                    'created_at' => date('d.m.Y H:i:s', $row['created_at'])
                )
            );
            return json_encode($response);
        } else {
            // No rows found
            $response = array(
                'success' => false,
                'message' => 'No records found'
            );
            return json_encode($response);
        }
        
    } catch(PDOException $e) {
        // Error occurred
        $response = array(
            'success' => false,
            'message' => $e->getMessage()
        );
        return json_encode($response);
    }
}

?>

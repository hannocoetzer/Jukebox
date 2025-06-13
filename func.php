<?php

if (isset($_POST['PlayServiceUpdate'])) {
        echo func1($_POST['PlayServiceUpdate']);
    }
	
 function func1($param){
	 
	 $request = json_decode($param);
	 
	 //echo $param2->playString;

try {
    // Create file "scandio_test.db" as database
    $db = new PDO('sqlite:play_stream.db');
    // Throw exceptions on error
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
  
    $sql = <<<SQL
CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY ,
    PlayString TEXT,
	PlayCommand TEXT,
    created_at INTEGER
)
SQL;
    $db->exec($sql);
  
    // Fix: Store time() result in a variable
    $currentTime = time();
  
    $sql = <<<SQL
INSERT INTO posts (PlayString,PlayCommand, created_at)
VALUES (:PlayString, :PlayCommand, :created_at)
SQL;
  
    $stmt = $db->prepare($sql);
    
    // Fix: Bind the actual values from the request, not the unused $data array
    $stmt->bindParam(':PlayString', $request->PlayString);
    $stmt->bindParam(':PlayCommand', $request->PlayCommand);
    $stmt->bindParam(':created_at', $currentTime);
    
    // Execute once with the actual data
    $stmt->execute();
  
    $result = $db->query('SELECT * FROM posts');
  
    foreach($result as $row) {
        // Fix: Include PlayCommand in the list destructuring
        list($id, $PlayString, $PlayCommand, $createdAt) = $row;
        $output  = "Id: $id <br/>\n";
        $output .= "PlayString: $PlayString<br/>\n";
        $output .= "PlayCommand: $PlayCommand<br/>\n";
        $output .= "Created at: ".date('d.m.Y H:i:s', $createdAt)."<br/>\n";
  
        echo $output;
    }
  
    //$db->exec("DROP TABLE posts");
} catch(PDOException $e) {
    echo $e->getMessage();  // Fix: Use getMessage() instead of getPlayString()
    echo $e->getTraceAsString();
}
 }

?>

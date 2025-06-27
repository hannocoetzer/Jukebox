<?php
// Enable error reporting for debugging
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Handle PlayServiceUpdate request
if (isset($_POST['PlayServiceUpdate'])) {
    echo func1($_POST['PlayServiceUpdate']);
    exit;
}

// Handle GetLastRow request
if (isset($_POST['GetLastRow'])) {
    echo getLastRow();
    exit;
}

function func1($param) {
    try {
        $request = json_decode($param, true); // decode as associative array
        
        if (!$request) {
            return "Error: Invalid JSON data";
        }

        // Create database connection
        $db = new PDO('sqlite:play_stream.db');
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Create table if not exists
        $sql = "CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            PlayString TEXT,
            PlayCommand TEXT,
            title TEXT,
            duration TEXT,
            streamUrl TEXT,
            created_at INTEGER
        )";
        $db->exec($sql);

        // Get last inserted ID
        $lastIdQuery = $db->query("SELECT id FROM posts ORDER BY id DESC LIMIT 1");
        $lastRecord = $lastIdQuery->fetch(PDO::FETCH_ASSOC);

        if (!$lastRecord) {
            return "Error: No records found to update";
        }

        $lastId = $lastRecord['id'];
        $currentTime = time();

        // Update the last record
        /* $sql = "UPDATE posts SET  */
        /*             PlayString = ?,  */
        /*             PlayCommand = ?,  */
        /*             title = ?,  */
        /*             duration = ?,  */
        /*             streamUrl = ?,  */
        /*             created_at = ? */
        /*         WHERE id = ?"; */
        /**/
        /* $stmt = $db->prepare($sql); */
        /* $stmt->execute([ */
        /*     $request['PlayString'] ?? '', */
        /*     $request['PlayCommand'] ?? '', */
        /*     $request['title'] ?? '', */
        /*     $request['duration'] ?? '', */
        /*     $request['streamUrl'] ?? '', */
        /*     $currentTime, */
        /*     $lastId */
        /* ]); */

                $sql = "UPDATE posts SET 
                    PlayString = ?, 
                    PlayCommand = ?, 
                    title = ? 
                WHERE id = ?";
        
        $stmt = $db->prepare($sql);
        $stmt->execute([
            $request['PlayString'] ?? '',
            $request['PlayCommand'] ?? '',
            $currentTime,
            $lastId
        ]);


        return "Record with ID $lastId updated successfully.";
        
    } catch(Exception $e) {
        return "Error: " . $e->getMessage();
    }
}



function getLastRow() {
    try {
        // Create database connection
        $db = new PDO('sqlite:play_stream.db');
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        // Get the last row
        $sql = "SELECT title, duration, streamUrl, created_at FROM posts ORDER BY id DESC LIMIT 1";
        $stmt = $db->query($sql);
        
        if ($row = $stmt->fetch(PDO::FETCH_ASSOC)) {
            $response = [
                'success' => true,
                'data' => [
                    'title' => $row['title'] ?? '',
                    'duration' => $row['duration'] ?? '',
                    'streamUrl' => $row['streamUrl'] ?? '',
                    'created_at' => date('d.m.Y H:i:s', $row['created_at'])
                ]
            ];
        } else {
            $response = [
                'success' => false,
                'message' => 'No records found'
            ];
        }
        
        return json_encode($response);
        
    } catch(Exception $e) {
        $response = [
            'success' => false,
            'message' => 'Error: ' . $e->getMessage()
        ];
        return json_encode($response);
    }
}

// Test function - remove this after testing
if (isset($_GET['test'])) {
    echo "PHP file is working!<br>";
    echo "Current time: " . date('Y-m-d H:i:s') . "<br>";
    
    // Test database connection
    try {
        $db = new PDO('sqlite:play_stream.db');
        echo "Database connection successful!<br>";
        
        // Check if table exists and has data
        $result = $db->query("SELECT COUNT(*) as count FROM posts");
        $count = $result->fetch()['count'];
        echo "Records in database: " . $count . "<br>";
        
    } catch(Exception $e) {
        echo "Database error: " . $e->getMessage() . "<br>";
    }
}
?>

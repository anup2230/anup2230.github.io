<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $name = $_POST["name"];
    $email = $_POST["email"];
    $subject = $_POST["subject"];
    $message = $_POST["message"];

    $to = "anup2230@gmail.com";
    $headers = "From: $name <$email>";
    $body = "Name: $name\nEmail: $email\n\nSubject: $subject\n\nMessage:\n$message";

    if (mail($to, $subject, $body, $headers)) {
        echo "Message sent successfully.";
    } else {
        echo "Message failed to send.";
    }
} else {
    echo "Invalid request";
}
?>
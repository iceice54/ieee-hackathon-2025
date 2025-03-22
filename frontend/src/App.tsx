import React, { useEffect, useRef, useState } from "react";
import axios from "axios";

import {
  Box,
  Button,
  TextField,
  Typography,
  Container,
  InputAdornment,
  AppBar,
  Toolbar,
  Skeleton,
} from "@mui/material";
import { FaPaperPlane } from "react-icons/fa";

interface Message {
  text: string;
  sender: "user" | "model";
}

function App() {
  const [input, setInput] = useState<string>("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isMessageSent, setIsMessageSent] = useState<boolean>(false);
  const [isLoading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement | null>(null);

  const handleMessageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInput(event.target.value);
  };

  const handlePrompt = async (prompt: string) => {
    setLoading(true);

    try {
      // const groupedMessages = {
      //   user: messages
      //     .filter((msg) => msg.sender === "user")
      //     .map((msg) => msg.text),
      //   model: messages
      //     .filter((msg) => msg.sender === "model")
      //     .map((msg) => msg.text),
      // };
      // const jsonString = JSON.stringify(groupedMessages);
      const res = await axios.post(
        "http://127.0.0.1:5000/prompt",
        { prompt },
        { headers: { "Content-Type": "application/json" } }
      );
      setMessages((prev) => [
        ...prev,
        { text: res.data.response, sender: "model" },
      ]);
      setLoading(false);
      // console.log(res.data);
      console.log(messages);
    } catch (err) {
      console.error(err);
    } finally {
    }
  };

  const handleSendClick = () => {
    console.log("Before calling API:", input); // Check what input is before calling
    if (input.trim()) {
      setIsMessageSent(true);
      handlePrompt(input);
      setInput(""); // Clear input after sending.
    }
  };

  const sendMessage = (text: string, sender: "user" | "model") => {
    if (!text.trim()) return;
    setMessages((prev) => [...prev, { text, sender }]);
  };

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
    <Container
      maxWidth={false}
      disableGutters
      sx={{
        height: "100vh",
        margin: "0px",
        justifyContent: "center",
      }}
    >
      <AppBar
        position="sticky"
        sx={{ backgroundColor: "#29867c", alignSelf: "baseline" }}
      >
        <Toolbar>
          <Typography
            variant="h6"
            sx={{ flexGrow: 1, textAlign: "center", fontSize: "30px" }}
          >
            Changentic AI
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        height="600px"
        width="100vw"
        bgcolor="#f5f5f5"
        marginTop="10px"
      >
        {/* Chatbot Title */}
        {isMessageSent && (
          <Box
            sx={{
              flex: 1, // Take up remaining space
              width: "70%",
              maxWidth: "70%",
              margin: "0",
              overflowY: "auto", // Enable scrolling for long conversations
              mb: 2,
            }}
          >
            {messages.map((msg, index) => (
              <Box
                key={index}
                sx={{
                  display: "flex",
                  justifyContent:
                    msg.sender === "user" ? "flex-end" : "flex-start",
                  marginRight: msg.sender === "user" ? "7px" : "0",
                  mb: 1,
                }}
              >
                <Typography
                  sx={{
                    bgcolor: msg.sender === "user" ? "#e0e0e0" : "#29867c",
                    color: msg.sender === "user" ? "black" : "white",
                    p: 1.5,
                    borderRadius: "10px",
                    maxWidth: "70%",
                    wordBreak: "break-word",
                    overflowWrap: "break-word",
                  }}
                >
                  {msg.text}
                </Typography>
              </Box>
            ))}
            {isLoading && (
              <Box sx={{ width: 400 }}>
                <Skeleton />
                <Skeleton animation="wave" />
                <Skeleton animation={false} />
                <Skeleton />
                <Skeleton animation={false} />
              </Box>
            )}
            <div ref={scrollRef} />
          </Box>
        )}
        {!isMessageSent && (
          <Typography variant="h3" color="#29867c" gutterBottom>
            Changentic AI
          </Typography>
        )}

        {/* Message Input and Send Button */}
        <Box
          display="flex"
          alignItems="center"
          justifyContent="center"
          width="100%"
          margin="0px"
        >
          <TextField
            variant="outlined"
            label="Ask a question"
            value={input}
            onChange={handleMessageChange}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                e.preventDefault();
                handleSendClick();
                sendMessage(input, "user");
              }
            }}
            multiline
            maxRows={6} // Maximum number of rows before scroll appear
            sx={{
              margin: 0,
              marginBottom: 3,
              width: "70%", // Adjust width here (e.g., 70% of the parent container)
            }}
            slotProps={{
              input: {
                endAdornment: (
                  <InputAdornment position="end">
                    <Button
                      onClick={() => {
                        handleSendClick();
                        sendMessage(input, "user");
                      }}
                      sx={{
                        width: "30px",
                        height: "40px",
                        backgroundColor: "#29867c",
                        color: "white",
                        "&:hover": {
                          backgroundColor: "#20665e ",
                        },
                      }}
                    >
                      <FaPaperPlane />
                    </Button>
                  </InputAdornment>
                ),
              },
            }}
          />
        </Box>
      </Box>
    </Container>
  );
}

export default App;

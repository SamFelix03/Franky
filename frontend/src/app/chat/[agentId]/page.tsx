'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Header from '@/components/ui/Header'
import ChatMessage, { Message, MessageRole } from '@/components/chat/ChatMessage'
import ChatInput from '@/components/chat/ChatInput'
import { motion } from 'framer-motion'
import { v4 as uuidv4 } from 'uuid'

export default function ChatPage() {
  const params = useParams()
  const agentId = params.agentId as string
  
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  
  // Load messages from local storage on initial render
  useEffect(() => {
    const storedMessages = localStorage.getItem(`chat-${agentId}`)
    if (storedMessages) {
      try {
        const parsedMessages = JSON.parse(storedMessages)
        // Convert string timestamps back to Date objects
        const messagesWithDates = parsedMessages.map((msg: any) => ({
          ...msg,
          timestamp: new Date(msg.timestamp)
        }))
        setMessages(messagesWithDates)
      } catch (error) {
        console.error('Failed to parse stored messages:', error)
      }
    } else {
      // Add welcome message if no history exists
      const welcomeMessage: Message = {
        id: uuidv4(),
        content: `Hello! I'm your AI assistant with access to DeFi tools. How can I help you today?`,
        role: 'assistant',
        timestamp: new Date()
      }
      setMessages([welcomeMessage])
    }
  }, [agentId])
  
  // Save messages to local storage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem(`chat-${agentId}`, JSON.stringify(messages))
    }
  }, [messages, agentId])
  
  // Handle sending a new message
  const handleSendMessage = async (content: string) => {
    // Create user message
    const userMessage: Message = {
      id: uuidv4(),
      content,
      role: 'user',
      timestamp: new Date()
    }
    
    // Add user message to chat
    setMessages(prev => [...prev, userMessage])
    
    // Show loading state
    setIsLoading(true)
    
    try {
      // In a real app, this would be an API call to your AI service
      // For now, we'll simulate a response after a delay
      setTimeout(() => {
        const assistantMessage: Message = {
          id: uuidv4(),
          content: getSimulatedResponse(content),
          role: 'assistant',
          timestamp: new Date()
        }
        
        setMessages(prev => [...prev, assistantMessage])
        setIsLoading(false)
      }, 1500)
    } catch (error) {
      console.error('Error getting response:', error)
      setIsLoading(false)
      
      // Add error message
      const errorMessage: Message = {
        id: uuidv4(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        role: 'assistant',
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, errorMessage])
    }
  }
  
  // Simple function to simulate AI responses
  const getSimulatedResponse = (userMessage: string): string => {
    const lowerCaseMessage = userMessage.toLowerCase()
    
    if (lowerCaseMessage.includes('swap') || lowerCaseMessage.includes('exchange')) {
      return "I can help you swap tokens using the 1inch protocol. What tokens would you like to exchange? For example, I can help you swap ETH for USDC."
    }
    
    if (lowerCaseMessage.includes('price') || lowerCaseMessage.includes('worth')) {
      return "Based on the latest data, ETH is currently trading at $3,245.67. Would you like me to check any other token prices?"
    }
    
    if (lowerCaseMessage.includes('gas') || lowerCaseMessage.includes('fee')) {
      return "Current gas prices on Ethereum:\n- Low: 25 gwei (~$2.50)\n- Average: 35 gwei (~$3.50)\n- High: 50 gwei (~$5.00)\n\nWould you like me to estimate gas costs for a specific transaction?"
    }
    
    if (lowerCaseMessage.includes('code') || lowerCaseMessage.includes('example')) {
      return "Here's an example of how to interact with the 1inch API using JavaScript:\n\n```javascript\nasync function getQuote(fromToken, toToken, amount) {\n  const response = await fetch(\n    `https://api.1inch.io/v5.0/1/quote?fromTokenAddress=${fromToken}&toTokenAddress=${toToken}&amount=${amount}`\n  );\n  return await response.json();\n}\n```\n\nYou can use this to get price quotes before executing a swap."
    }
    
    return "I understand you're asking about " + userMessage.substring(0, 30) + "... How can I assist you with that using my DeFi tools?"
  }
  
  return (
    <main className="min-h-screen flex flex-col">
      <Header />
      
      <div className="flex-1 container mx-auto px-4 pt-24 pb-6 flex flex-col">
        <motion.div 
          className="mb-4 flex items-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <div className="w-10 h-10 rounded-full bg-[var(--primary-green)]/20 flex items-center justify-center mr-3">
            <span className="text-[var(--primary-green)]">🤖</span>
          </div>
          <div>
            <h1 className="text-xl font-bold gradient-text">Agent #{agentId}</h1>
            <p className="text-sm text-[var(--text-secondary)]">Powered by UserName</p>
          </div>
        </motion.div>
        
        <div className="flex-1 bg-black/30 rounded-xl cyberpunk-border overflow-hidden flex flex-col">
          {/* Messages container */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message, index) => (
              <ChatMessage 
                key={message.id} 
                message={message} 
                isLatest={index === messages.length - 1} 
              />
            ))}
            
            {/* Scroll anchor */}
            <div className="h-4" />
          </div>
          
          {/* Input area */}
          <ChatInput 
            onSendMessage={handleSendMessage} 
            isLoading={isLoading} 
          />
        </div>
      </div>
    </main>
  )
} 
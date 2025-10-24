import {
  Body,
  Container,
  Head,
  Heading,
  Html,
  Img,
  Preview,
  Section,
  Text,
} from '@react-email/components';

interface GiftReceivedEmailProps {
  user_name?: string;
  sender_name?: string;
  gift_message?: string;
  order_number?: string;
}

export const GiftReceivedEmail = ({
  user_name = 'User',
  sender_name = 'Someone special',
  gift_message = 'Hope you like it! 💝',
  order_number = 'GIFT-12345',
}: GiftReceivedEmailProps) => {
  return (
    <Html>
      <Head />
      <Preview>{sender_name} sent you a gift!</Preview>
      <Body style={main}>
        <Container style={container}>
          {/* Logo */}
          <Section style={logoSection}>
            <Img
              src="https://crushme.com.co/static/frontend/BUY.png"
              width="120"
              height="120"
              alt="CrushMe"
              style={logo}
            />
          </Section>

          {/* Title */}
          <Heading style={heading}>You have a gift!</Heading>

          {/* Greeting */}
          <Text style={text}>Hello {user_name},</Text>

          {/* Main message */}
          <Text style={textHighlight}>
            <strong>{sender_name}</strong> sent you a gift through CrushMe.
          </Text>

          {/* Sender's message */}
          {gift_message && (
            <Section style={messageBox}>
              <Text style={messageLabel}>Message from {sender_name}:</Text>
              <Text style={messageText}>"{gift_message}"</Text>
            </Section>
          )}

          {/* Order number */}
          <Section style={orderSection}>
            <Text style={orderLabel}>Order number</Text>
            <Text style={orderNumberText}>{order_number}</Text>
          </Section>

          {/* Special note */}
          <Section style={noteBox}>
            <Text style={noteText}>
              We'll notify you when your gift is shipped. We hope you enjoy it! 💝
            </Text>
          </Section>

          {/* Footer */}
          <Text style={footer}>
            Want to thank {sender_name}? Send them a message on CrushMe.
          </Text>

          <Text style={footerSmall}>
            CrushMe · Medellín, Colombia
          </Text>
        </Container>
      </Body>
    </Html>
  );
};

const main = {
  backgroundColor: '#FFFFFF',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
};

const container = {
  margin: '0 auto',
  padding: '40px 20px',
  maxWidth: '600px',
};

const logoSection = {
  textAlign: 'center' as const,
  margin: '0 0 30px 0',
};

const logo = {
  margin: '0 auto',
};

const emoji = {
  fontSize: '64px',
  textAlign: 'center' as const,
  margin: '0 0 20px 0',
  display: 'block',
};

const heading = {
  fontSize: '28px',
  fontWeight: '600',
  color: '#D689A2',
  textAlign: 'center' as const,
  margin: '0 0 30px 0',
  lineHeight: '1.3',
};

const text = {
  fontSize: '16px',
  color: '#4B5563',
  lineHeight: '1.6',
  margin: '0 0 20px 0',
};

const textHighlight = {
  fontSize: '16px',
  color: '#4B5563',
  lineHeight: '1.6',
  margin: '0 0 30px 0',
  textAlign: 'center' as const,
};

const messageBox = {
  backgroundColor: '#FAF3F3',
  padding: '24px',
  borderRadius: '12px',
  margin: '30px 0',
  borderLeft: '4px solid #FF3FD5',
};

const messageLabel = {
  fontSize: '14px',
  color: '#6B7280',
  margin: '0 0 12px 0',
  fontWeight: '600',
};

const messageText = {
  fontSize: '16px',
  color: '#11181E',
  fontStyle: 'italic' as const,
  lineHeight: '1.6',
  margin: '0',
};

const orderSection = {
  textAlign: 'center' as const,
  margin: '30px 0',
  padding: '20px',
  backgroundColor: '#F9FAFB',
  borderRadius: '8px',
};

const orderLabel = {
  fontSize: '12px',
  color: '#6B7280',
  textTransform: 'uppercase' as const,
  letterSpacing: '0.5px',
  margin: '0 0 8px 0',
};

const orderNumberText = {
  fontSize: '18px',
  color: '#11181E',
  fontWeight: '600',
  margin: '0',
};

const noteBox = {
  backgroundColor: '#FFF7ED',
  padding: '20px',
  borderRadius: '8px',
  margin: '30px 0',
};

const noteText = {
  fontSize: '14px',
  color: '#92400E',
  textAlign: 'center' as const,
  margin: '0',
  lineHeight: '1.5',
};

const footer = {
  fontSize: '14px',
  color: '#9CA3AF',
  textAlign: 'center' as const,
  margin: '40px 0 10px 0',
  paddingTop: '40px',
  borderTop: '1px solid #E5E7EB',
};

const footerSmall = {
  fontSize: '12px',
  color: '#D1D5DB',
  textAlign: 'center' as const,
  margin: '0',
};

GiftReceivedEmail.PreviewProps = {
  user_name: 'Maria',
  sender_name: 'Carlos',
  gift_message: 'Happy birthday! Hope you love this gift 🎉💝',
  order_number: 'GIFT-87654',
} as GiftReceivedEmailProps;

export default GiftReceivedEmail;

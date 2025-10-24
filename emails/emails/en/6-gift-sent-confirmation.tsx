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

interface GiftSentConfirmationEmailProps {
  user_name?: string;
  receiver_name?: string;
  order_number?: string;
}

export const GiftSentConfirmationEmail = ({
  user_name = 'User',
  receiver_name = 'Recipient',
  order_number = 'GIFT-12345',
}: GiftSentConfirmationEmailProps) => {

  return (
    <Html>
      <Head />
      <Preview>Your gift for {receiver_name} has been confirmed</Preview>
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
          <Heading style={heading}>Gift sent successfully!</Heading>

          {/* Greeting */}
          <Text style={text}>Hello {user_name},</Text>

          {/* Main message */}
          <Text style={textHighlight}>
            Your gift for <strong>{receiver_name}</strong> has been confirmed and is being processed.
          </Text>

          {/* Order number */}
          <Section style={orderSection}>
            <Text style={orderLabel}>Order number</Text>
            <Text style={orderNumberText}>{order_number}</Text>
          </Section>

          {/* Special note */}
          <Section style={noteBox}>
            <Text style={noteText}>
              {receiver_name} will receive a notification about your gift. We'll let you know when it's shipped. 🎁
            </Text>
          </Section>

          {/* Footer */}
          <Text style={footer}>
            Thank you for making someone special happy with CrushMe.
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

GiftSentConfirmationEmail.PreviewProps = {
  user_name: 'Carlos',
  receiver_name: 'Maria',
  order_number: 'GIFT-87654',
} as GiftSentConfirmationEmailProps;

export default GiftSentConfirmationEmail;

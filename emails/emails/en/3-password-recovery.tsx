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

interface PasswordRecoveryEmailProps {
  user_name?: string;
  code?: string;
}

export const PasswordRecoveryEmail = ({
  user_name = 'User',
  code = '1234',
}: PasswordRecoveryEmailProps) => {
  return (
    <Html>
      <Head />
      <Preview>Your recovery code is {code}</Preview>
      <Body style={main}>
        <Container style={container}>
          {/* Logo */}
          <Section style={logoSection}>
            <Img
              src="https://crushme.com.co/static/frontend/BUY.png"
              width="140"
              height="140"
              alt="CrushMe"
              style={logo}
            />
          </Section>

          {/* Title */}
          <Heading style={heading}>Recover your password</Heading>

          {/* Greeting */}
          <Text style={text}>Hello {user_name},</Text>

          {/* Main message */}
          <Text style={text}>
            We received a request to reset your password. Use the following code to continue:
          </Text>

          {/* Recovery code */}
          <Section style={codeSection}>
            <Text style={codeStyle}>{code}</Text>
          </Section>

          {/* Note */}
          <Text style={note}>
            This code will expire in 15 minutes.
          </Text>

          {/* Security note */}
          <Text style={securityNote}>
            If you didn't request a password reset, ignore this email. Your password will remain unchanged.
          </Text>

          {/* Footer */}
          <Text style={footer}>
            For your security, never share this code with anyone.
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
  margin: '0 0 40px 0',
};

const logo = {
  margin: '0 auto',
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

const codeSection = {
  textAlign: 'center' as const,
  margin: '40px 0',
};

const codeStyle = {
  fontSize: '48px',
  fontWeight: '700',
  color: '#FF3FD5',
  letterSpacing: '8px',
  margin: '0',
  padding: '20px',
  backgroundColor: '#FAF3F3',
  borderRadius: '12px',
  display: 'inline-block',
};

const note = {
  fontSize: '14px',
  color: '#6B7280',
  textAlign: 'center' as const,
  margin: '0 0 30px 0',
};

const securityNote = {
  fontSize: '14px',
  color: '#6B7280',
  textAlign: 'center' as const,
  margin: '0 0 40px 0',
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

PasswordRecoveryEmail.PreviewProps = {
  user_name: 'Carlos',
  code: '9163',
} as PasswordRecoveryEmailProps;

export default PasswordRecoveryEmail;

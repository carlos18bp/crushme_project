/**
 * 1. Registro de Usuario - Código de Verificación
 * Estilo: Minimalista elegante inspirado en Tidal
 */

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

interface SignupVerificationEmailProps {
  user_name?: string;
  code?: string;
}

export const SignupVerificationEmail = ({
  user_name = 'Usuario',
  code = '1234',
}: SignupVerificationEmailProps) => {
  return (
    <Html>
      <Head />
      <Preview>Tu código de verificación es {code}</Preview>
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

          {/* Título */}
          <Heading style={heading}>Verifica tu cuenta</Heading>

          {/* Saludo */}
          <Text style={text}>Hola {user_name},</Text>

          {/* Mensaje principal */}
          <Text style={text}>
            Gracias por registrarte en CrushMe. Para completar tu registro, usa el siguiente código de verificación:
          </Text>

          {/* Código de verificación */}
          <Section style={codeSection}>
            <Text style={codeStyle}>{code}</Text>
          </Section>

          {/* Nota */}
          <Text style={note}>
            Este código expirará en 10 minutos.
          </Text>

          {/* Footer */}
          <Text style={footer}>
            Si no creaste esta cuenta, puedes ignorar este correo.
          </Text>

          <Text style={footerSmall}>
            CrushMe · Medellín, Colombia
          </Text>
        </Container>
      </Body>
    </Html>
  );
};

// Estilos minimalistas inspirados en Tidal
const main = {
  backgroundColor: '#ffffff',
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
};

const container = {
  margin: '0 auto',
  padding: '40px 20px',
  maxWidth: '560px',
};

const logoSection = {
  textAlign: 'center' as const,
  marginBottom: '40px',
};

const logo = {
  margin: '0 auto',
};

const heading = {
  fontSize: '28px',
  fontWeight: '600',
  color: '#11181E',
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
  margin: '0 0 40px 0',
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

SignupVerificationEmail.PreviewProps = {
  user_name: 'Carlos',
  code: '8472',
} as SignupVerificationEmailProps;

export default SignupVerificationEmail;

/**
 * 3. Recuperación de Contraseña
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

interface PasswordRecoveryEmailProps {
  user_name?: string;
  code?: string;
}

export const PasswordRecoveryEmail = ({
  user_name = 'Usuario',
  code = '1234',
}: PasswordRecoveryEmailProps) => {
  return (
    <Html>
      <Head />
      <Preview>Tu código de recuperación es {code}</Preview>
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
          <Heading style={heading}>Recupera tu contraseña</Heading>

          {/* Saludo */}
          <Text style={text}>Hola {user_name},</Text>

          {/* Mensaje principal */}
          <Text style={text}>
            Recibimos una solicitud para restablecer tu contraseña. Usa el siguiente código para continuar:
          </Text>

          {/* Código de recuperación */}
          <Section style={codeSection}>
            <Text style={codeStyle}>{code}</Text>
          </Section>

          {/* Nota */}
          <Text style={note}>
            Este código expirará en 15 minutos.
          </Text>

          {/* Nota de seguridad */}
          <Text style={securityNote}>
            Si no solicitaste restablecer tu contraseña, ignora este correo. Tu contraseña permanecerá sin cambios.
          </Text>

          {/* Footer */}
          <Text style={footer}>
            Por tu seguridad, nunca compartas este código con nadie.
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

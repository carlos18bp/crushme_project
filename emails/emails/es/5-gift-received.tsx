/**
 * 5. Regalo Recibido
 * Estilo: Minimalista elegante inspirado en Tidal
 */

import {
  Body,
  Column,
  Container,
  Head,
  Heading,
  Hr,
  Html,
  Img,
  Preview,
  Row,
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
  user_name = 'Usuario',
  sender_name = 'Alguien especial',
  gift_message = '¡Espero que te guste! 💝',
  order_number = 'GIFT-12345',
}: GiftReceivedEmailProps) => {
  return (
    <Html>
      <Head />
      <Preview>¡{sender_name} te ha enviado un regalo!</Preview>
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

          {/* Título */}
          <Heading style={heading}>¡Tienes un regalo!</Heading>

          {/* Saludo */}
          <Text style={text}>Hola {user_name},</Text>

          {/* Mensaje principal */}
          <Text style={textHighlight}>
            <strong>{sender_name}</strong> te ha enviado un regalo a través de CrushMe.
          </Text>

          {/* Mensaje del remitente */}
          {gift_message && (
            <Section style={messageBox}>
              <Text style={messageLabel}>Mensaje de {sender_name}:</Text>
              <Text style={messageText}>"{gift_message}"</Text>
            </Section>
          )}

          {/* Número de orden */}
          <Section style={orderSection}>
            <Text style={orderLabel}>Número de orden</Text>
            <Text style={orderNumberText}>{order_number}</Text>
          </Section>

          {/* Nota especial */}
          <Section style={noteBox}>
            <Text style={noteText}>
              Te notificaremos cuando tu regalo sea enviado. ¡Esperamos que lo disfrutes! 💝
            </Text>
          </Section>

          {/* Footer */}
          <Text style={footer}>
            ¿Quieres agradecer a {sender_name}? Envíale un mensaje en CrushMe.
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
  maxWidth: '600px',
};

const logoSection = {
  textAlign: 'center' as const,
  marginBottom: '20px',
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
  fontSize: '18px',
  color: '#11181E',
  lineHeight: '1.6',
  margin: '0 0 30px 0',
  textAlign: 'center' as const,
};

const messageBox = {
  backgroundColor: '#FAF3F3',
  padding: '24px',
  borderRadius: '12px',
  borderLeft: '4px solid #FF3FD5',
  margin: '30px 0',
};

const messageLabel = {
  fontSize: '12px',
  color: '#9CA3AF',
  textTransform: 'uppercase' as const,
  letterSpacing: '0.5px',
  margin: '0 0 8px 0',
};

const messageText = {
  fontSize: '18px',
  color: '#11181E',
  fontStyle: 'italic',
  lineHeight: '1.6',
  margin: '0',
};

const giftInfoBox = {
  backgroundColor: '#F9FAFB',
  padding: '20px',
  borderRadius: '8px',
  margin: '30px 0',
};

const sectionTitle = {
  fontSize: '14px',
  color: '#9CA3AF',
  textTransform: 'uppercase' as const,
  letterSpacing: '0.5px',
  margin: '0 0 16px 0',
};

const itemRow = {
  marginBottom: '12px',
};

const itemName = {
  fontSize: '16px',
  color: '#11181E',
  margin: '0',
};

const itemQuantity = {
  fontSize: '16px',
  color: '#6B7280',
  margin: '0',
};

const divider = {
  borderColor: '#E5E7EB',
  margin: '30px 0',
};

const shippingSection = {
  margin: '30px 0',
};

const addressText = {
  fontSize: '16px',
  color: '#4B5563',
  lineHeight: '1.6',
  margin: '0',
};

const orderSection = {
  textAlign: 'center' as const,
  margin: '30px 0',
};

const orderLabel = {
  fontSize: '12px',
  color: '#9CA3AF',
  textTransform: 'uppercase' as const,
  letterSpacing: '0.5px',
  margin: '0 0 4px 0',
};

const orderNumberText = {
  fontSize: '18px',
  color: '#11181E',
  fontWeight: '600',
  margin: '0',
};

const noteBox = {
  backgroundColor: '#FEF3C7',
  padding: '16px 20px',
  borderRadius: '8px',
  margin: '30px 0',
};

const noteText = {
  fontSize: '14px',
  color: '#92400E',
  margin: '0',
  lineHeight: '1.5',
  textAlign: 'center' as const,
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
  user_name: 'María',
  sender_name: 'Carlos',
  gift_message: '¡Feliz cumpleaños! Espero que te encante este regalo 🎉💝',
  order_number: 'GIFT-87654',
} as GiftReceivedEmailProps;

export default GiftReceivedEmail;

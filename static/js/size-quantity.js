$(document).ready(function () {

    $('#id_size_0').attr('checked', true);
    $(".quantity_50").html("S/.50");
    {
        #$(".savings_50").html("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
        #
    }
    $(".quantity_100").html("S/.70");
    $(".savings_100").html("Ahorra 30%");
    $(".quantity_200").html("S/.90");
    $(".savings_200").html("Ahorra 55%");
    $(".quantity_300").html("S/.108");
    $(".savings_300").html("Ahorra 64%");
    $(".quantity_500").html("S/.140");
    $(".savings_500").html("Ahorra 78%");
    $('input:radio[name="size"]').change(function () {
        if ($(this).val() == '5cm x 5cm') {
            $(".quantity_50").html("S/.50");
            {
                #$(".savings_50").html("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
                #
            }
            $(".quantity_100").html("S/.70");
            $(".savings_100").html("Ahorra 30%");
            $(".quantity_200").html("S/.90");
            $(".savings_200").html("Ahorra 55%");
            $(".quantity_300").html("S/.108");
            $(".savings_300").html("Ahorra 64%");
            $(".quantity_500").html("S/.140");
            $(".savings_500").html("Ahorra 78%");
        } else if ($(this).val() == '7cm x 7cm') {
            $(".quantity_50").html("S/.70");
            {
                #$(".savings_50").html("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
                #
            }
            $(".quantity_100").html("S/.90");
            $(".savings_100").html("Ahorra 36%");
            $(".quantity_200").html("S/.130");
            $(".savings_200").html("Ahorra 54%");
            $(".quantity_300").html("S/.160");
            $(".savings_300").html("Ahorra 69%");
            $(".quantity_500").html("S/.240");
            $(".savings_500").html("Ahorra 66%");
        } else if ($(this).val() == '10cm x 10cm') {
            $(".quantity_50").html("S/.90");
            {
                #$(".savings_50").html("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
                #
            }
            $(".quantity_100").html("S/.115");
            $(".savings_100").html("Ahorra 36%");
            $(".quantity_200").html("S/.180");
            $(".savings_200").html("Ahorra 50%");
            $(".quantity_300").html("S/.280");
            $(".savings_300").html("Ahorra 48%");
            $(".quantity_500").html("S/.450");
            $(".savings_500").html("Ahorra 50%");
        } else if ($(this).val() == '13cm x 13cm') {
            $(".quantity_50").html("S/.200");
            {
                #$(".savings_50").html("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
                #
            }
            $(".quantity_100").html("S/.370");
            $(".savings_100").html("Ahorra 10%");
            $(".quantity_200").html("S/.430");
            $(".savings_200").html("Ahorra 46%");
            $(".quantity_300").html("S/.500");
            $(".savings_300").html("Ahorra 58%");
            $(".quantity_500").html("S/.900");
            $(".savings_500").html("Ahorra 55%");
        }
    });

});

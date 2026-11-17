ParticleDef()
{
	LifeTime()
	{
		keyf(0, 1.5)
	}

	GravityMul()
	{
		randf(0, 1.6, 1.8)
	}

	Drag()
	{
		randf(0, 9, 10)
	}

	Color()
	{
		keyv4(0, 0.55, 0.55, 0.55, 0.46)
		keyv4(0.17, 0.55, 0.55, 0.55, 0.3956)
		keyv4(0.27, 0.55, 0.55, 0.55, 0.2438)
		keyv4(0.47, 0.55, 0.55, 0.55, 0.115)
		keyv4(1, 0.55, 0.55, 0.55, 0.0552)
		keyv4(1.2, 0.55, 0.55, 0.55, 0.046)
		keyv4(1.5, 0.55, 0.55, 0.55, 0)
	}

	Size()
	{
		keyf(0, 42)
		keyf(1.5, 74)
	}

	Align("on_start")

	AspectRatio()
	{
		randf(0, 1, 1)
	}

	Material("IRN_BloodSplatWS_particleBLEND.mat", "IRN_BloodSplatWS_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}

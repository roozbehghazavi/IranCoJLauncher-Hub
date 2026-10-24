ParticleDef()
{
	LifeTime()
	{
		keyf(0, 0.8)

	}

	Material("BloodTrail_particleMUL.mat", "BloodTrail_particleMUL.mat")

	Size()
	{

		randf(0, 10, 10)
                randf(0.8, 20, 45)
		
	}

	Color()
	{
		keyv4(0,   1, 1, 1, 1)
		keyv4(0.4,   1, 1, 1, 1)
		keyv4(0.8,   1, 1, 1, 0)


	}

	GravityMul()
	{

		keyf(0, 0.5)
	}

	Rotation()
	{

		randf(0, 0, 360)
		randf(1, 0, 360)

	}

	Drag()
	{
		keyf(0, 1)
	}






}

